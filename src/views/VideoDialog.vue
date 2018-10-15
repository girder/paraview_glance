<template lang="pug">
v-dialog(v-model="dialog", :width="width")
  template(slot="activator")
    slot(name="activator")
  iframe.responsive(
      v-if="dialog"
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
  opacity .82
.v-dialog
  background-color black
  @media (max-width: 600px)
    .responsive
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
</style>
