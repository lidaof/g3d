<template>
  <div class="about">
    <h1>About</h1>
    <p>
      Back to
      <router-link to="/">Home</router-link>
    </p>
    <div>
      <p>
        This online Genomic 3D Visualizer is developed by
        <a href="http://wang.wustl.edu/">Ting Wang Lab</a> at
        <a href="https://wustl.edu/">Washington University in St. Louis</a>. We
        used <a href="https://vuejs.org/">Vue.js</a> as the framework and
        <a href="https://threejs.org/">three.js</a> as the drawing engine.
      </p>

      <p>
        To run a local copy, first install
        <a href="https://nodejs.org/en/">Node.js</a>, then get the code from our
        repository:
      </p>
      <code>git clone https://github.com/lidaof/g3d.git</code>
      <p>
        Navigate to the
        <code>g3dv</code> directory, and install the dependent packages, after
        that, start running this tool:
      </p>
      <code>
        cd g3d/g3dv
        <br />npm install <br />npm run serve
      </code>
      <p>
        Your local mirror can be accessed from
        <a href="http://localhost:8080/">http://localhost:8080/</a>.
      </p>
      <p>
        If you have any problem or suggestion, please contact us by submit an
        <a href="https://github.com/lidaof/g3d/issues">issue request</a>. Thank
        you in advance!
      </p>
    </div>
  </div>
</template>
