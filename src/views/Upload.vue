<template lang="pug">
.upload-wrapper
  .dropzone-wrapper(
      v-if="!files.length", :class="dropzoneClass", @dragenter="dropzoneClass = 'animate'",
      @dragleave="dropzoneClass = null", @drop="dropzoneClass = null")
    .dropzone-message
      v-icon(size="50px") attach_file
      .title.mt-3 {{ dropzoneMessage }}
    input.file-input(type="file", :multiple="multiple", @change="filesChanged")

  .pb-2.px-3(v-show="files.length && !errorMessage")
    v-subheader(v-show="!uploading") {{ statusMessage }}

    v-text-field(v-if="!uploading", v-model="folderName", label="Name your timelapse sequence",
        hint="Optional")

    v-btn(v-if="!uploading", color="warning", @click="files = []")
      v-icon.mr-1 close
      | Clear all
    v-btn(v-if="!uploading", color="success", @click="$emit('start', folderName)")
      v-icon.mr-1 play_arrow
      | Start upload

  div(v-if="errorMessage")
    v-alert(:value="true", type="error")
      span.body-2.mr-2 {{ errorMessage }}
      v-btn(v-if="!uploading", color="purple darken-1", dark, @click="$emit('resume')")
        v-icon.mr-1 replay
        | Resume upload

  div(v-if="uploading")
    .subheading.px-3.
      {{ formatDataSize(totalProgress) }} / {{ formatDataSize(totalSize) }}
      ({{ totalProgressPercent }}%)
    v-progress-linear(:value="totalProgressPercent", height="20")

  div(v-show="files.length")
    v-alert(v-if="!uploading", type="info", :value="true").
      You must sort these files into the correct order prior to uploading them. Drag and drop
      the files to re-order them.

    v-list
      draggable(v-model="files", :options="draggableOpts")
        v-list-tile.file-tile(v-for="(file, i) in files", :key="file.file.name", avatar,
            :class="`status-${file.status}`")
          v-list-tile-avatar
            v-btn.mx-0(v-if="file.status === 'pending'", icon, @click="removeFile(i)")
              v-icon close
            v-progress-circular(v-if="file.status === 'uploading'", color="primary", :rotate="-90",
                :value="progressPercent(file.progress)",
                :indeterminate="file.progress.indeterminate")
            v-icon(v-if="file.status === 'done'", color="success", large) check
            v-icon(v-if="file.status === 'error'", color="error", large) warning
          v-list-tile-avatar(tile)
            .img-preview.mr-2
              img(v-if="file.file.type.indexOf('image/') === 0", :src="imgSrc(file.file)")
              .no-preview(v-else) N/A
          v-list-tile-content
            v-list-tile-title {{ file.file.name }}
            v-list-tile-sub-title
              span(v-if="file.progress.current") {{ formatDataSize(file.progress.current ) }} /
              span  {{ formatDataSize(file.file.size) }}
</template>

<script>
import draggable from 'vuedraggable';
import { sizeFormatter } from '../utils/mixins';
import { ResourceIcons } from '../constants';

export default {
  components: { draggable },
  mixins: [sizeFormatter],
  props: {
    errorMessage: {
      default: null,
      type: String,
    },
    multiple: {
      default: true,
      type: Boolean,
    },
    uploading: {
      default: false,
      type: Boolean,
    },
  },
  data: () => ({
    files: [],
    folderName: '',
    dragover: false,
    dropzoneClass: null,
    ResourceIcons,
    draggableOpts: {
      ghostClass: 'g-drag-ghost',
      animation: 80,
    },
  }),
  computed: {
    dropzoneMessage() {
      if (this.multiple) {
        return 'Drag files here or click to select them';
      }
      return 'Drag a file here or click to select one';
    },
    statusMessage() {
      return `${this.files.length} selected (${this.formatDataSize(this.totalSize)} total)`;
    },
    totalProgress() {
      return this.files.reduce((v, f) => v + (f.progress.current || 0), 0);
    },
    totalSize() {
      return this.files.reduce((v, f) => v + f.file.size, 0);
    },
    totalProgressPercent() {
      return this.progressPercent({
        current: this.totalProgress,
        total: this.totalSize,
      });
    },
  },
  methods: {
    filesChanged({ target }) {
      this.files = [...target.files].map(file => ({
        file,
        status: 'pending',
        progress: {},
        upload: null,
        result: null,
      }));
    },
    imgSrc(file) {
      return window.URL.createObjectURL(file);
    },
    progressPercent(progress) {
      if (!progress.total) {
        return 0;
      }
      return Math.round((100 * (progress.current || 0)) / progress.total);
    },
    removeFile(i) {
      this.files.splice(i, 1);
    },
  },
};
</script>

<style lang="stylus" scoped>
$stripeColor = #f0f0f3
$img = linear-gradient(
  -45deg, $stripeColor 25%, transparent 25%, transparent 50%, $stripeColor 50%,
  $stripeColor 75%, transparent 75%, transparent)

.dropzone-wrapper
  position relative
  cursor pointer
  min-height 260px
  height 100%
  text-align center
  background-color #f6f6f9
  background-repeat repeat
  background-size 30px 30px

  &:hover
    background-image $img

  &.animate
    animation stripes 2s linear infinite
    background-image $img

  .file-input
    position absolute
    top 0
    right 0
    bottom 0
    left 0
    height 100%
    width 100%
    opacity 0
    z-index 1
    cursor pointer

@keyframes stripes
  from
    background-position 0 0
  to
    background-position 30px 60px

.dropzone-message
  position absolute
  left 50%
  top 50%
  transform translateX(-50%) translateY(-50%)

.file-tile
  background-color transparent
  transition width 0.8s ease-in-out 1s, height 0.8s ease-in-out 1s, background .5s ease-in-out
  width 100%
  height 100%

  &.status-uploading
    background-color #fef4c9

  &.status-done
    width 0
    height 0
    overflow hidden

.upload-wrapper
  display flex
  flex-direction column
  height 100%

.img-preview
  >img
    width 56px
    height 56px
  .no-preview
    width 56px
    height 56px
    color white
    background-color black
    line-height 56px

.g-drag-ghost
  background-color #fcf2c7
</style>
