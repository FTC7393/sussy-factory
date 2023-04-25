<script>
  import { onMount } from "svelte";
  import * as THREE from "three";
  import { STLLoader } from "three/examples/jsm/loaders/STLLoader.js";
  import { OrbitControls } from "three/examples/jsm/controls/OrbitControls";

  export let stlFile = '';
  export let color = '';
  let fileinput;
  let stlSize = { x: 0, y: 0, z: 0 };
  let stlVolume = 0.0;

  // Necessary for camera/plane rotation
  let degree = Math.PI / 180;

  // Create scene
  const scene = new THREE.Scene();
  scene.background = null

  onMount(() => {
    const renderer = new THREE.WebGLRenderer({
      canvas: document.querySelector("canvas"),
      alpha: true
    });

    // There's no reason to set the aspect here because we're going
    // to set it every frame anyway so we'll set it to 2 since 2
    // is the the aspect for the canvas default size (300w/150h = 2)
    const camera = new THREE.PerspectiveCamera(100, 2, 1, 1000);
    camera.position.z = 20; //change z and y to change figure size in view
    camera.position.y = 20; //
    camera.position.x = 20;
    camera.rotation.x = -45 * degree;

    // Add controls, targetting the same DOM element
    let controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 0, 0);
    controls.rotateSpeed = 0.5;
    controls.autoRotate = true;
    controls.minDistance = 20;
    controls.maxDistance = 200;
    controls.update();

    //stop autorotate when clicked
    document.querySelector("canvas").addEventListener('mousedown', () => {
      controls.autoRotate = false;
    });
    document.querySelector("canvas").addEventListener('touchstart', () => {
      controls.autoRotate = false;
    });

    // Plane
    // Ground (comment out line: "scene.add( plane );" if Ground is not needed...)
    // var plane = new THREE.Mesh(
    //   new THREE.PlaneGeometry(500, 500),
    //   new THREE.MeshPhongMaterial({
    //     color: 0x999999,
    //     specular: 0x101010
    //   })
    // );
    // plane.rotation.x = -90 * degree;
    // plane.position.y = -25;
    // plane.receiveShadow = true;
    // scene.add(plane);

    // Lighting
    const frontSpot = new THREE.SpotLight(0xeeeece, 0.5, 0);
    frontSpot.position.set(1000, 1000, -1000);
    scene.add(frontSpot);

    const frontSpot2 = new THREE.SpotLight(0xddddce, 1, 0);
    frontSpot2.position.set(-500, -500, -500);
    scene.add(frontSpot2);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    function resizeCanvasToDisplaySize() {
      const canvas = renderer.domElement;
      const width = canvas.clientWidth;
      const height = canvas.clientHeight;
      if (canvas.width !== width || canvas.height !== height) {
        // you must pass false here or three.js sadly fights the browser
        renderer.setSize(width, height, false);
        camera.aspect = width / height;
        camera.updateProjectionMatrix();

        // set render target sizes here
      }
    }
    resizeCanvasToDisplaySize();

    // Create an animate function, which will allow you to render your scene and define any movements
    const animate = function() {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
      // resizeCanvasToDisplaySize();
    };
    animate();
  });

  // https://stackoverflow.com/questions/13853301/why-doesnt-filereader-pass-file-to-loader-load-used-by-three-js-scene
  const loadStl = () => {
    console.log(stlFile)
    if (stlFile === '') return;
    fetch(stlFile).then(res => res.blob()).then(res => {

      // console.log(res)
      let reader = new FileReader();
      // let fileObject = e.target.files[0];

      reader.onload = function() {
        // console.log(this.result)

        var loader = new STLLoader();
        //console.log(this.result);
        var geometry = loader.parse(this.result)
        geometry.computeVertexNormals(true);
        // var geometry = loader.load(stlFile,
    // function (geometry) {
    //     const mesh = new THREE.Mesh(geometry, material)
    //     scene.add(mesh)
    // },
    // (xhr) => {
    //     console.log((xhr.loaded / xhr.total) * 100 + '% loaded')
    // },
    // (error) => {
    //     console.log(error)
    // });
        //get stil volume
        getSize(geometry);
        getVolume(geometry);

        const material = new THREE.MeshPhongMaterial({
          color: color,
          specular: 0x111111,
          shininess: 200,
        });

        var mesh = new THREE.Mesh(geometry, material);
        mesh.name = "loadedMeshObject";
        mesh.castShadow = true;
        mesh.receiveShadow = true;

        // model offset
        mesh.position.set(0, -25, 0);
        // modal orientation on load

        mesh.rotation.x = THREE.MathUtils.degToRad(-90);
        mesh.rotation.z = THREE.MathUtils.degToRad(210);

        // scene.remove(scene.getObjectByName('model'));
        // mesh.name = 'model';
        // Add loaded model to scene
        scene.add(mesh);
      };
      reader.readAsArrayBuffer(res);
      // console.log("File Object:", fileObject);
    });
  };


  $: stlFile, loadStl()
  $: color, loadStl()

  function getSize(geometry) {
    let size = new THREE.Vector3();
    geometry.computeBoundingBox();
    geometry.boundingBox.getSize(size);
    //console.log("Size:", size)
    return (stlSize = size);
  }

  function getVolume(geometry) {
    let position = geometry.attributes.position;
    let faces = position.count / 3;
    let sum = 0;
    let p1 = new THREE.Vector3(),
      p2 = new THREE.Vector3(),
      p3 = new THREE.Vector3();
    for (let i = 0; i < faces; i++) {
      p1.fromBufferAttribute(position, i * 3 + 0);
      p2.fromBufferAttribute(position, i * 3 + 1);
      p3.fromBufferAttribute(position, i * 3 + 2);
      sum += signedVolumeOfTriangle(p1, p2, p3);
    }
    //console.log(sum)
    return (stlVolume = sum);
  }

  function signedVolumeOfTriangle(p1, p2, p3) {
    return p1.dot(p2.cross(p3)) / 6.0;
  }

  // Clear file input
  function clearFileInput(ctrl) {
    try {
      ctrl.value = null;
    } catch (ex) {}
    if (ctrl.value) {
      ctrl.parentNode.replaceChild(ctrl.cloneNode(true), ctrl);
    }
  }

  // Rest the Scene and clear file
  function resetScene() {
    const object = scene.getObjectByName("loadedMeshObject");
    stlSize = { x: 0, y: 0, z: 0 };
    stlVolume = 0.0;
    scene.remove(object);
    clearFileInput(fileinput);
  }

</script>

<canvas class="rounded w-full h-full"></canvas>

