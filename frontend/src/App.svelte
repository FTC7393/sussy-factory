<svelte:head>
  <title>eV 7393's amogus emporium!</title>
  <!-- <script type="module" src="https://unpkg.com/@google/model-viewer/dist/model-viewer.min.js"></script> -->

</svelte:head>

<script>
  import Canvas from "../src/lib/Canvas.svelte";
  import "./app.css";

  let state = 'loading';

  let team;
  let status;
  let stl_url;
  let phone;

  var initial_camera_state = null;

  function test() {
  }

  function load_model() {
    // stl_viewer = new StlViewer(document.getElementById("stl_cont"), {models: [{id: 0, filename: stl_url}], model_loaded_callback: load_callback, auto_rotate: true});
  }

  function load_callback() {
    //reset the camera to the initial state, or store the initial state if it isn't set up yet
    if (initial_camera_state === null) {
        initial_camera_state = stl_viewer.get_camera_state();
    } else {
        stl_viewer.set_camera_state(initial_camera_state);
    }

    //rotate to the correct position from the initial camera state to get a good view of the text
    stl_viewer.rotate(0, Math.PI/2, Math.PI, -0.5);
    stl_viewer.set_auto_rotate(true);

    myRequest('/color_of_the_day', (res) => {
        document.getElementById('color_of_the_day').style.backgroundColor = res;
        document.getElementById('color_of_the_day').innerText = res;
        stl_viewer.set_color(0, res)
    });
  }

  fetch("/user_initial_info")
  .then(res => res.json())
  .then(json => {
    team = json[0];
    status = json[1];
    stl_url = json[2];
    phone = json[3];

    if (team === '') {
      state = 'info';
    } else {
      state = 'customize';
      load_model();
    }
  });
  function save_info() {
    console.log(team)
    fetch(`/team?team=${encodeURIComponent(team)}&phone=${encodeURIComponent(phone)}`)
    .then(res => {
      if (res === 'invalid') {
          alert('invalid phone number, please try again');
          res = '';
      }
      phone = res; //sanatized phone number is returned
      state = 'customize';
      load_model();

      //TODO option to go back and change team/phone
    });

  }
</script>

<Canvas stlFile="/stl_src/default-amogus-ev-7393.stl" />

{#if state === 'loading'}
Loading...
{:else if state === 'info'}
<label>team/name (e.g. FTC 7393 or Joe Schmoe): <input type="text" id="team" name="team" bind:value="{team}" /></label>
<label>(optional) phone number to be notified when the print is done (SMS charges may apply): <input type="text" id="phone" name="phone" bind:value="{phone}" /></label>
<button on:click={save_info}>next</button>

{:else if state === 'customize'}
TODO customize your among us figurine<br/>
download STL: <a id="download" href="{stl_url}">{stl_url}</a>

{:else if state === 'confirm'}
TODO review the figurine and confirm you want to submit it to print
{:else if state === 'waiting'}
TODO this page will update once your figurine is printed
(if phone number:) you will recieve a text message
{:else if state === 'printed'}
TODO your figurine has printed, come pick it up
{:else if state === 'taken'}
TODO you have picked up your figurine
{:else}
error
{/if}


<div id="stl_cont" style="width: 100vw; height: 80vh; overflow: hidden;"></div>


<hr>

<h1>Hello world!</h1>
<ul>
  <li>team: {team}</li>
  <li>status: {status}</li>
  <li>stl_url: {stl_url}</li>
  <li>phone: {phone}</li>
</ul>
<button on:click={test}>test</button>
