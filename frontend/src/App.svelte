<svelte:head>
  <title>eV 7393's amogus emporium!</title>
	<link rel='icon' type='image/png' href='/favicon.png'>
</svelte:head>

<style>
input:checked + svg {
  display: block;
}

@font-face {
  font-family: "amogus";
  src: url("/font/Amongus-3zjxX.ttf");
}
.font-amogus {
  font-family: "amogus", "Roboto", serif;
  font-size: 3em;
  letter-spacing: 0.1em;
  line-height: 1.2;
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
  let top_text = '';
  let bottom_text = '';
  let shoes = false;
  let generated = false;
  let submitted = false;
  let expired = false;
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
    expired = json.expired;

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
    } else if (submitted) {
      if (taken) {
        state = 'taken';
      } else if (printed) {
        state = 'printed';
      } else {
        state = 'waiting';
      }
    } else if (expired) {
      state = 'expired';
    } else if (generated) {
      state = 'review';
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
        } else if (res === 'expired') {
          alert("Sorry, your QR code has expired.")
          state = 'expired';
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
    if (state === 'waiting' || state === 'printed' || state === 'expired') {
      fetch('/user/info')
      .then(res => res.json())
      .then(json => {
        console.log(json)
        decode_user_info(json);
        if (state === 'expired' && !expired) {
          state = 'customize';
        }
        // if (printed && !taken) {
        if (printed && !have_alerted_for_print_done) {
          have_alerted_for_print_done = true;
          state = 'printed';
          setTimeout(
            () => alert("Your 3D print is done! Go pick it up from FTC 7393's pit area."),
            500
          );
        }
        if (taken) {
          state = 'taken';
        }
      });
    }
  }

  setInterval(loop, 5000);
</script>

<div class="flex flex-col sm:flex-row m-0 min-h-screen" style="background-image: url('/img/background.png'); background-size: cover 100%; background-repeat: repeat-x;">
  <MenuBar />
  <div class="mx-auto">
  {#if state === 'loading'}
    <h1>Loading...</h1>

  {:else if state === 'info'}
    <div class="flex flex-col space-y-3 p-4">
      <div class="font-amogus font-bold text-2xl">
        Enter Your Info
      </div>

      <div class="flex flex-col">
        <div class="font-medium">Team/Name (e.g. FTC 7393 or Joe Schmoe): </div>
        <input class="px-4 input border border-gray-400 appearance-none rounded w-full py-2 focus focus:border-lmao-yellow focus:outline-none active:outline-none active:border-lmao-yellow" type="text" id="team" name="team" bind:value="{team}" />

      </div>
      <div class="flex flex-col">
        <div class="font-medium">(optional) Phone Number to be notified when the print is done (SMS charges may apply): </div>
        <input class="px-4 input border border-gray-400 appearance-none rounded w-full py-2 focus focus:border-lmao-yellow focus:outline-none active:outline-none active:border-lmao-yellow" type="text" id="phone" name="phone" bind:value="{phone}" />

      </div>
      <!-- <button class="transition py-2 sm:px-4 bg-lmao-yellow dark:text-gray-800 shadow-2xl rounded-md m-4 text-center" on:click={save_info}><div class="font-bold">next</div></button> -->
      <!-- <button class="m-auto flex w-fit py-9 px-10 font-bold" style="background: url(/img/arrow.png) no-repeat;" on:click={save_info}>Next</button> -->
      <button class="flex flex-col m-auto font-bold transition p-4 bg-lmao-yellow dark:text-gray-800 shadow-2xl rounded-md" on:click={save_info}>
        <img class="m-auto" alt="proceed" src="/img/proceed.png" />
      </button>
    </div>

  {:else if state === 'customize'}
    <div class="flex-col p-4">
      <div class="flex flex-row">
        <div class="font-amogus font-bold text-2xl">
          Customize Figurine
        </div>
      </div>

      <div class="flex flex-row">

        <div class="flex flex-col w-7/12">
          <div class="flex flex-col">
            <div class="font-medium">Top Text</div>
            <input
              type="text"
              id="top_text"
              name="top_text"
              bind:value={top_text}
              class="input border border-gray-400 appearance-none rounded w-full px-3 py-3 pt-2 pb-2 focus focus:border-lmao-yellow focus:outline-none active:outline-none active:border-lmao-yellow"
            />
          </div>
          <div class="flex flex-col">
            <div class="font-medium">Bottom Text (optional): </div>
            <input
              type="text"
              id="bottom_text"
              name="bottom_text"
              bind:value={bottom_text}
              class="input border border-gray-400 appearance-none rounded w-full px-3 py-3 pt-2 pb-2 focus focus:border-lmao-yellow focus:outline-none active:outline-none active:border-lmao-yellow"
            />
          </div>

          <label class="flex justify-start items-start my-3">
            <div class="bg-white border-2 rounded border-gray-400 w-6 h-6 flex flex-shrink-0 justify-center items-center mr-2 focus-within:border-blue-500">
              <input type="checkbox" id="shoes" name="shoes" bind:checked={shoes} class="opacity-0 absolute">
              <svg class="fill-current hidden w-4 h-4 text-green-500 pointer-events-none" viewBox="0 0 20 20"><path d="M0 11l2-2 5 5L18 3l2 2L7 18z"></path></svg>
            </div>
            <div class="select-none font-medium">Drip Shoes?</div>
          </label>
          <!-- <div class="flex-grow"></div> -->
          <div class="flex flex-col space-y-3">
            <button on:click={generate} class="font-bold transition py-2 bg-lmao-yellow dark:text-gray-800 shadow-2xl rounded-md text-center">
              generate preview
              <!-- <img class="m-auto" alt="customize" src="/img/customize.png" /> -->
            </button>
            <button class="font-medium transition py-2 bg-gray-300 dark:text-gray-800 shadow-2xl rounded-md text-center" on:click={edit_info}>
              edit team info
            </button>
            <p class="font-bold">NOTE: More than 6 characters per row will be unreadable!</p>
            <p class="font-medium">color of the day: <span style:background={color_of_the_day_hex}>{color_of_the_day_hex} <span style="color: white">{color_of_the_day_hex}</span></span></p>
          </div>
        </div>
        <div class="w-5/12 lg:h-auto">
          <Canvas stlFile={stl_url} color={color_of_the_day} />
        </div>
      </div>
      <details>
        <summary class="font-medium py-2">add special chars</summary>
        <p class="font-medium">This uses the Roboto font, so some unicode characters are available. Here's a few of them for more convenient copy/paste:</p>
        <p class="font-normal" style="font-family: Roboto;">⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉¼½¾©®™¡¢£¤¥¦§¨ª«¬¯°±´µ¶·¸º»¿×æ÷ʭΔΘεφ҈҉†‡•‣․‥…›※‼‽‾‿⁀⁁⁂⁃⁄⁊⁋⁌⁍⁎⁏⁐⁑⁕⁖⁘⁙⁚⁛⁜⁝⁞√∞∫≈≠≤≥␣◊⸎⸙⸚ꙮ</p>
      </details>
      <a href="{stl_url}" class="flex flex-col transition p-2 bg-gray-300 dark:text-gray-800 shadow-2xl rounded-md text-center w-full">
        <div>
          download STL (to print yourself instead)
        </div>
      </a>
    </div>

  {:else if state === 'generating'}
    <div class="p-4">
      <div class="font-amogus font-bold text-2xl">
        Generating Preview
      </div>
      <p class="font-medium">This will usually take about 10-20 seconds.</p>
      <img style="width: min(90vw, 500px)" alt="tablet upload task among us" src="/img/among-us-upload.gif" /><br/><br/>
    </div>

  {:else if state === 'review'}
    <div class="flex flex-col p-4">
      <div class="font-amogus font-bold text-2xl">
        Review Figurine
      </div>

      <div class="flex flex-row">
        <div class="flex flex-col basis-1/2 space-y-3">
          <div class="font-medium w-full py-1">
            Review the model and either submit it to be 3D printed, or continue customizing.
          </div>
        <button class="flex flex-row font-bold transition py-2 bg-lmao-yellow dark:text-gray-800 shadow-2xl rounded-md text-center" on:click={customize}>
            <!-- edit -->
            <img class="m-auto" alt="customize" src="/img/customize.png" />
          </button>
          <button class="font-bold transition py-2 bg-lmao-yellow dark:text-gray-800 shadow-2xl rounded-md text-center" on:click={submit}>
            submit
          </button>

          <div class="font-medium">
            spots left in print queue: {queue_spots_left}
          </div>
          <!-- <a href="{stl_url}" class="transition py-2 sm:px-4 bg-lmao-yellow dark:text-gray-800 shadow-2xl rounded-md m-4 text-center">
            download STL
          </a> -->
        </div>
        <div class="w-1/2 lg:h-auto">
          <Canvas stlFile={stl_url} color={color_of_the_day} />
        </div>
      </div>
    </div>

  {:else if state === 'waiting'}
    <div class="p-4">
      <div class="font-amogus font-bold text-2xl">
        Waiting for Figurine to be Printed
      </div>
      <p class="font-medium my-2">Submitted successfully.</p>
      <p class="font-medium my-2">Keep this page open, an alert will pop up when your figurine is ready to pick up.</p>
      {#if phone}
        <p class="font-medium my-2">You will also recieve a text message at the number you provided earlier.</p>
      {:else}
        <p class="font-bold my-2">You can also provide a phone number to get a text message when your print is done.</p>
      {/if}
      <button class="font-bold my-2 transition py-2 bg-lmao-yellow dark:text-gray-800 shadow-2xl rounded-md text-center w-full" on:click={edit_info}>edit phone number</button>
      <img class="w-full p-10 max-w-xl" alt="" src="/img/radio.png" />
    </div>

  {:else if state === 'printed'}
    <div>
      <div  class="p-4">
        <div class="font-amogus font-bold text-2xl">
          Done Printing!
        </div>
        <p class="font-medium my-2">Your figurine has printed, come pick it up from FTC 7393's pit area.</p>
      </div>
      <img alt="done" src="/img/done.png" class="w-full" />
    </div>

  {:else if state === 'taken'}
    <div class="p-4">
      <div class="font-amogus font-bold text-2xl">
        Thanks :]
      </div>
      <div class="flex flex-col w-full">
        <img alt="thumbs up" src="/img/amongs-up.png" class="w-20 block m-auto my-4" />
      </div>
      <p class="font-medium my-2">Thank you for picking up your print from our pit area!</p>
      <p class="font-medium my-2">You can't make any more print requests, but you can still customize a figurine, download the STL, and print it yourself. (Or just admire the 3D preview :)</p>
      <button class="font-bold my-2 transition py-2 bg-lmao-yellow dark:text-gray-800 shadow-2xl rounded-md text-center w-full" on:click={customize}>back to generator</button>
    </div>

  {:else if state === 'expired'}
    <div class="p-4">
      <div class="font-amogus font-bold text-2xl">
        Expired :(
      </div>
      <div class="flex flex-col w-full">
        <img alt="among us ghost" src="/img/yellow-ghost.png" class="w-20 block m-auto my-4" />
      </div>
      <p class="font-medium my-2">Unfortunately your QR code has expired.</p>
      <p class="font-medium my-2">You can still customize a figurine, download the STL, and print it yourself. (Or just admire the 3D preview :)</p>
      <button class="font-bold my-2 transition py-2 bg-lmao-yellow dark:text-gray-800 shadow-2xl rounded-md text-center w-full" on:click={customize}>back to generator</button>
    </div>

  {:else}
    <h1>Error invalid state: {state}. Please reload the page.</h1>

  {/if}
  </div>
</div>
