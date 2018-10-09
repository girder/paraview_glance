<template lang="pug">
v-dialog(v-model="dialog", :width="width")
  template(slot="activator")
    slot(name="activator")
  iframe(v-if="dialog"
      :src="src",
      :width="width",
      :height="height",
      frameborder="0",
      webkitallowfullscreen,
      mozallowfullscreen,
      allowfullscreen)
</template>

<script>
export default {
  props: {
    src: {
      type: String,
      required: true,
    },
    width: {
      type: Number,
      required: true,
    },
    height: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      dialog: false,
    };
  },
};
</script>

<style lang="stylus">
.v-overlay--active:before
  opacity .82 !important
.v-dialog
  background-color black
</style>
