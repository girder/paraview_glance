import os
from girder import events
from girder.api import access
from girder.api.describe import Description, autoDescribeRoute
from girder.api.rest import Resource, filtermodel
from girder.constants import AccessType
from girder.models.collection import Collection
from girder.models.folder import Folder
from girder.models.item import Item
from girder.utility import setting_utilities
from girder.utility.server import staticFile
from girder.utility.plugin_utilities import registerPluginWebroot


class PluginSettings(object):
    STUDIES_COLL_ID = 'stroke_ct.studies_collection_id'


class Study(Resource):
    def __init__(self):
        super(Study, self).__init__()
        self.resourceName = 'study'

        self.route('GET', (), self.listStudies)
        self.route('POST', (), self.createStudy)

    @access.public
    @filtermodel(Folder)
    @autoDescribeRoute(
        Description('List studies.')
        .pagingParams(defaultSort='studyId', defaultLimit=500)
    )
    def listStudies(self, limit, offset, sort):
        cursor = Folder().find({'studyId': {'$exists': True}}, sort=sort)
        return list(Folder().filterResultsByPermission(
            cursor, level=AccessType.READ, user=self.getCurrentUser(), limit=limit, offset=offset))

    @access.user
    @filtermodel(Folder)
    @autoDescribeRoute(
        Description('Create a new study.')
        .param('identifier', 'The unique ID of the study.')
        .param('date', 'Study date.', dataType='dateTime')
        .param('modality', 'Study modality.')
        .param('description', 'Study description.')
    )
    def createStudy(self, identifier, date, modality, description):
        user = self.getCurrentUser()
        study = Folder().createFolder(
            parent=user, name=identifier, description=description, parentType='user', public=False,
            creator=user, allowRename=True)
        study['isStudy'] = True
        study['nSeries'] = 0
        study['studyDate'] = date
        study['studyId'] = identifier
        study['studyModality'] = modality
        return Folder().save(study)


class Series(Resource):
    def __init__(self):
        super(Series, self).__init__()
        self.resourceName = 'series'

        self.route('POST', (), self.createSeries)

    @access.user
    @filtermodel(Item)
    @autoDescribeRoute(
        Description('Create a new series.')
        .modelParam('studyId', 'The parent study.', model=Folder, level=AccessType.WRITE,
                    paramType='query')
        .param('name', 'The name of the series.')
        .param('preset', 'Volume rendering preset to use.', required=False)
    )
    def createSeries(self, study, name):
        series = Item().createItem(name, creator=self.getCurrentUser(), folder=study)
        series['isSeries'] = True
        series = Item().save(series)

        Folder().update({
            '_id': study['_id']
        }, {
            'nSeries': {'$increment': 1}
        }, multi=False)

        return series


def _itemDeleted(event):
    item = event.info
    if item.get('isSeries') is True:
        Folder().update({
            '_id': item['folderId']
        }, {
            'nSeries': {'$increment': -1}
        }, multi=False)


@setting_utilities.validator(PluginSettings.STUDIES_COLL_ID)
def _validateStudiesColl(doc):
    Collection().load(doc['value'], exc=True, force=True)


def load(info):
    webroot = staticFile(os.path.join(info['pluginRootDir'], 'dist', 'index.html'))
    registerPluginWebroot(webroot, info['name'])

    info['config']['/stroke_ct_static'] = {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': os.path.join(info['pluginRootDir'], 'dist', 'stroke_ct_static')
    }

    info['apiRoot'].study = Study()
    info['apiRoot'].series = Series()

    Folder().ensureIndex(([('studyId', 1)], {'sparse': True}))
    Folder().exposeFields(level=AccessType.READ, fields={
        'isStudy', 'nSeries', 'studyDate', 'studyId', 'studyModality'})
    Item().exposeFields(level=AccessType.READ, fields={'isSeries'})

    events.bind('model.item.remove', info['name'], _itemDeleted)
