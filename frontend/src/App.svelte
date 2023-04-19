<svelte:head>
  <title>eV 7393's amogus emporium!</title>
	<link rel='icon' type='image/png' href='/favicon.png'>
</svelte:head>

<style>
input:checked + svg {
  display: block;
}

@tailwind base;
@tailwind components;
@tailwind utilities;
</style>


<script>
  import Canvas from "../src/lib/Canvas.svelte";
  import MenuBar from "./lib/MenuBar.svelte";

  let state = 'loading';

  let team;
  let status;
  let stl_url;
  let phone;
  let printed;
  let taken;
  let color_of_the_day;
  let color_of_the_day_hex;
  let top_text = 'eV';
  let bottom_text = '7393';
  let shoes = false;
  let generated = false;
  let submitted = false;
  let have_alerted_for_print_done = false;
  let queue_spots_left = 'Loading...';

  fetch('/color_of_the_day').then(res => res.text()).then(res => {
    color_of_the_day_hex = res;
    color_of_the_day = parseInt(color_of_the_day_hex.replace('#', '0x'));
  });


  function decode_user_info(json) {
    team = json.team;
    status = json.status;
    stl_url = json.stl_url;
    phone = json.phone;
    printed = json.printed;
    taken = json.taken;
    if (json.stl_options) {
      if (json.stl_options.top_text) top_text = json.stl_options.top_text;
      if (json.stl_options.bottom_text) bottom_text = json.stl_options.bottom_text;
      if (json.stl_options.shoes) shoes = json.stl_options.shoes;
    }

    generated = status === 'generated';
    submitted = status === 'submitted';
  }

  fetch('/user/info')
  .then(res => res.json())
  .then(json => {
    console.log(json)
    decode_user_info(json);

    if (status === 'default') {
      if (team === '') {
        state = 'info';
      } else {
        state = 'customize';
      }
    } else if (generated) {
      state = 'review';
    } else if (submitted) {
      if (taken) {
        state = 'taken';
      } else if (printed) {
        state = 'printed';
      } else {
        state = 'waiting';
      }
    }
  });
  function save_info() {
    console.log(team)
    if (team === '') {
      alert('team/name required')
    } else {
      fetch(`/team?team=${encodeURIComponent(team)}&phone=${encodeURIComponent(phone)}`)
      .then(res => res.text())
      .then(res => {
        if (res === 'invalid') {
          alert('invalid phone number, please try again');
          res = '';
        } else {
          phone = res; //sanatized phone number is returned
          if (taken) {
            state = 'taken';
          } else if (submitted) {
            state = 'waiting';
          } else {
            state = 'customize';
          }
        }
      });
    }
  }

  function edit_info() {
    state = 'info';
  }

  function generate() {
    if (top_text.length >= 10 || bottom_text.length >= 10) {
      if (!confirm('You have entered 10 or more characters on a row, which is too detailed for the 3D printer to make and will be unreadable. Are you sure you want to generate anyway?')) {
        return;
      }
    }
    state = 'generating';
    console.log(`/gen_stl?top_text=${encodeURIComponent(top_text)}&bottom_text=${encodeURIComponent(bottom_text)}&shoes=${encodeURIComponent(shoes)}`);
    fetch(`/gen_stl?top_text=${encodeURIComponent(top_text)}&bottom_text=${encodeURIComponent(bottom_text)}&shoes=${encodeURIComponent(shoes)}`)
    .then((res) => {
      if (res.ok) {
        return res.text();
      } else {
        state = 'customize';
        alert('failed to generate preview');
        // throw new Error('failed to generate preview');
      }
    })
    .then(res => {
      stl_url = res;
      if (taken) {
        state = 'customize';
      } else {
        state = 'review';
      }
    })
    .catch((error) => {
      console.log(error)
    });
  }

  function customize() {
    state = 'customize';
  }
  function submit() {
    if (confirm("Are you sure you want to submit the current model? You can only submit once and you cannot change anything after.")){
      fetch('/submit').then(res => res.text()).then(res => {
        if (res === 'already submitted') {
          alert('You already submitted a model, you may not change it after.');
          state = 'waiting';
          submitted = true;
        } else if (res === 'queue full') {
          alert("The print queue is full. Try again tomorrow, or stop by FTC 7393's pit to pick up a non-custom figurine.");
          state = 'customize';
        } else {
          alert('Submitted successfully.');
          state = 'waiting';
          submitted = true;
        }
      });
    // } else {
      // state = 'customize';
    }
  }

  function loop() {
    if (state === 'review') {
      fetch('/queue_spots_left')
      .then(res => res.text())
      .then(res => queue_spots_left = res);
    }
    if (state === 'waiting' || state === 'printed') {
      console.log('print done?')

      fetch('/user/info')
      .then(res => res.json())
      .then(json => {
        console.log(json)
        decode_user_info(json);
        // if (printed && !taken) {
        if (printed && !have_alerted_for_print_done) {
          alert("Your 3D print is done! Go pick it up from FTC 7393's pit area.")
          have_alerted_for_print_done = true;
          state = 'printed';
        }
        if (taken) {
          state = 'taken';
        }
      });
    }
  }

  setInterval(loop, 5000);
</script>


<div class=" flex flex-col w-auto h-full sm:flex-row sm:min-h-screen ">

  <MenuBar></MenuBar>
  {#if state === 'loading'}
  <h1>Loading...</h1>

  {:else if state === 'info'}
    <div class="flex flex-col space-y-3">
      <div class="font-bold text-2xl mt-2">Enter Your Info</div>

      <div class="flex flex-col mx-4">
        <div class="font-bold">team/name (e.g. FTC 7393 or Joe Schmoe): </div>
        <input class="px-6 input border border-gray-400 appearance-none rounded w-full px-3 py-3 focus focus:border-lmao-yellow focus:outline-none active:outline-none active:border-lmao-yellow" type="text" id="team" name="team" bind:value="{team}" />

      </div>
      <div class="flex flex-col mx-4">
        <div class="font-bold">(optional) phone number to be notified when the print is done (SMS charges may apply): </div>
        <input class="px-6 input border border-gray-400 appearance-none rounded w-full px-3 py-3 focus focus:border-lmao-yellow focus:outline-none active:outline-none active:border-lmao-yellow" type="text" id="phone" name="phone" bind:value="{phone}" />

      </div>

    </div>

    <button on:click={save_info}>next</button>

  {:else if state === 'customize'}
    <div class="flex flex-row">
      <div class="font-bold text-2xl">
        Customize Your Figurine
      </div>
    </div>

    <div class="flex flex-row">

      <div class="flex flex-col">
        <div class="flex flex-col">
          <div>top text</div>
          <input
            type="text"
            id="top_text"
            name="top_text"
            bind:value={top_text}
            class="input border border-gray-400 appearance-none rounded w-full px-3 py-3 pt-5 pb-2 focus focus:border-lmao-yellow focus:outline-none active:outline-none active:border-lmao-yellow"
          />
        </div>
        <div class="flex flex-col">
          <div>bottom text (optional): </div>
          <input
            type="text"
            id="bottom_text"
            name="bottom_text"
            bind:value={bottom_text}
            class="input border border-gray-400 appearance-none rounded w-full px-3 py-3 pt-2 pb-2 focus focus:border-lmao-yellow focus:outline-none active:outline-none active:border-lmao-yellow"
          />
        </div>

        <label class="flex justify-start items-start">
          <div class="bg-white border-2 rounded border-gray-400 w-6 h-6 flex flex-shrink-0 justify-center items-center mr-2 focus-within:border-blue-500">
            <input type="checkbox" id="shoes" name="shoes" bind:checked={shoes} class="opacity-0 absolute">
            <svg class="fill-current hidden w-4 h-4 text-green-500 pointer-events-none" viewBox="0 0 20 20"><path d="M0 11l2-2 5 5L18 3l2 2L7 18z"></path></svg>
          </div>
          <div class="select-none">Drip Shoes?</div>
        </label>
        <div class="flex-grow"></div>
        <div class="flex flex-col space-y-3 mx-3">
          <button on:click={generate} class="transition flex flex-row items-center items-center sm:px-4 bg-lmao-yellow dark:text-gray-800 shadow-2xl rounded-md">
            customize
          </button>
          <button class="transition flex flex-row items-center items-center sm:px-4 bg-lmao-yellow dark:text-gray-800 shadow-2xl rounded-md" on:click={edit_info}>
            edit team info
          </button>
        </div>


      </div>
      <Canvas stlFile={stl_url} color={color_of_the_day} />


    </div>
    <p>If no bottom text is provided, the top text will be moved to the middle.</p>
    <p style="font-weight: bold">NOTE: Any more than 6 characters on a row will likely be unreadable!</p>
    <details>
    <summary>special chars</summary>
    <p>This uses the Roboto font, so some unicode characters are available. Here's a few of them for more convenient copy/paste:</p>
    <p style="font-family: Roboto;">⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉¼½¾©®™¡¢£¤¥¦§¨ª«¬¯°±´µ¶·¸º»¿×æ÷ʭΔΘεφ҈҉†‡•‣․‥…›※‼‽‾‿⁀⁁⁂⁃⁄⁊⁋⁌⁍⁎⁏⁐⁑⁕⁖⁘⁙⁚⁛⁜⁝⁞√∞∫≈≠≤≥␣◊⸎⸙⸚ꙮ</p>
    </details>
    <p>color of the day: <span style:background={color_of_the_day_hex}>{color_of_the_day_hex} <span style="color: white">{color_of_the_day_hex}</span></span></p>
    <br/>



  {:else if state === 'generating'}
  <h1>Generating 3D Preview...</h1>
  <p>This will usually take about 10-20 seconds.</p>
  <img style="width: min(90vw, 500px)" alt="tablet upload task among us" src="/img/among-us-upload.gif" /><br/><br/>
  

  {:else if state === 'review'}
  <div class="font-bold">
    Review Your Figurine
  </div>

  <div class="flex flex-row">
    <div class="flex flex-col basis-1/2">
      <button class="transition flex flex-row items-center px-2 sm:px-4 space-x-1 5s:space-x-2 bg-lmao-yellow dark:text-gray-800 shadow-2xl rounded-md" on:click={customize}>
        edit
      </button>
      <button class="transition flex flex-row items-center px-2 sm:px-4 space-x-1 5s:space-x-2 bg-lmao-yellow dark:text-gray-800 shadow-2xl rounded-md" on:click={submit}>
        submit
      </button>

      <div class="font-semibold w-full py-1 sm:p-0 text-lg sm:text-2xl ">
        Review the figurine and confirm you want to submit it to be 3D printed. You cannot make any changes after submitting.
      </div>

      <div class="font-bold">
        spots left in print queue: {queue_spots_left}
      </div>
      <a id="download" href="{stl_url} " class="transition flex flex-row items-center px-2 sm:px-4 space-x-1 5s:space-x-2 bg-lmao-yellow dark:text-gray-800 shadow-2xl rounded-md">
        download STL
      </a>
    </div>

  <Canvas stlFile={stl_url} color={color_of_the_day} class=""/>
  </div>



  {:else if state === 'waiting'}
  <h1>Waiting for Figurine to be Printed</h1>
  <p>Submitted successfully. Keep this page open, an alert will pop up when your figurine is ready to pick up.</p>
    {#if phone}
      You will also recieve a text message at the number you provided earlier.
    {:else}
      You can also provide a phone number to get a text message when your print is done.
    {/if}
    <button on:click={edit_info}>edit phone number</button>

  {:else if state === 'printed'}
  <h1>Done Printing!</h1>
  Your figurine has printed, come pick it up from FTC 7393's pit area.

  {:else if state === 'taken'}
  <h1>Done :]</h1>
  <p>Thank you for picking up your print from our pit area!</p>
  <p>You can't make any more print requests, but you can still customize a figurine, download the STL, and print it yourself. (Or just admire the 3D preview :)</p>
  <button on:click={customize}>back to generator</button>

  {:else}
  Error invalid state: {state}. Please reload the page.

  {/if}
</div>
