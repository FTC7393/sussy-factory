<svelte:head>
  <title>eV 7393's amogus emporium!</title>
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
  import { text } from "svelte/internal";
import Canvas from "../src/lib/Canvas.svelte";
  import MenuBar from "./lib/MenuBar.svelte";

  let state = 'customize';

  let stl_url = '/stl_src/default-amogus-ev-7393.stl';
  let color = '#FF0000'; //'#FAD67E';
  let top_text = '';
  let bottom_text = '';
  let shoes = false;
  let settings_changed = false;

  function generate() {
    if (top_text.length >= 10 || bottom_text.length >= 10) {
      if (!confirm('You have entered 10 or more characters on a row, which is too detailed for the 3D printer to make and will be unreadable. Are you sure you want to generate anyway?')) {
        return;
      }
    }
    state = 'generating';
    console.log(`/gen_stl2?top_text=${encodeURIComponent(top_text)}&bottom_text=${encodeURIComponent(bottom_text)}&shoes=${encodeURIComponent(shoes)}`);
    fetch(`/gen_stl2?top_text=${encodeURIComponent(top_text)}&bottom_text=${encodeURIComponent(bottom_text)}&shoes=${encodeURIComponent(shoes)}`)
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
      settings_changed = false;
      state = 'customize';
    })
    .catch((error) => {
      console.log(error)
    });
  }
  function change() {
    settings_changed = true;
  }
</script>

<div class="flex flex-col sm:flex-row m-0 min-h-screen" style="background-image: url('/img/background.png'); background-size: cover 100%; background-repeat: repeat-x;">
  <MenuBar />
  <div class="mx-auto">

  {#if state === 'customize'}
    <div class="flex-col p-4">
      <div class="flex flex-row">
        <div class="font-amogus font-bold text-2xl">
          Sussy Factory
        </div>
      </div>
      <div class="font-medium">
        Customize an among us figurine, and download an STL file to print it yourself.
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
              on:change={change}
              on:keydown={change}
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
              on:change={change}
              on:keydown={change}
              class="input border border-gray-400 appearance-none rounded w-full px-3 py-3 pt-2 pb-2 focus focus:border-lmao-yellow focus:outline-none active:outline-none active:border-lmao-yellow"
            />
          </div>

          <label class="flex justify-start items-start my-3">
            <div class="bg-white border-2 rounded border-gray-400 w-6 h-6 flex flex-shrink-0 justify-center items-center mr-2 focus-within:border-blue-500">
              <input
                type="checkbox"
                id="shoes"
                name="shoes"
                bind:checked={shoes} 
                on:change={change}
                class="opacity-0 absolute"
              />
              <svg class="fill-current hidden w-4 h-4 text-green-500 pointer-events-none" viewBox="0 0 20 20"><path d="M0 11l2-2 5 5L18 3l2 2L7 18z"></path></svg>
            </div>
            <div class="select-none font-medium">Drip Shoes?</div>
          </label>
          <!-- <div class="flex-grow"></div> -->
          <div class="flex flex-col space-y-3">
            {#if settings_changed}
              <button on:click={generate} class="font-bold transition py-2 bg-lmao-yellow dark:text-gray-800 shadow-2xl rounded-md text-center">
                generate STL
                <!-- <img class="m-auto" alt="customize" src="/img/customize.png" /> -->
              </button>
            {:else}
              <!-- <button class="font-medium transition py-2 bg-lmao-yellow dark:text-gray-800 shadow-2xl rounded-md text-center" on:click={alert}>
                download STL (to print yourself)
              </button> -->
              <a href="{stl_url}" class="font-bold transition py-2 bg-lmao-yellow dark:text-gray-800 shadow-2xl rounded-md text-center">
                <div>
                  download STL (to print yourself)
                </div>
              </a>
            {/if}
            <p class="font-bold">NOTE: More than 6 characters per row will be unreadable unless you print at a larger scale!</p>
            <label>color: <input type="color" bind:value={color}></label>
          </div>
        </div>
        <div class="w-5/12 lg:h-auto">
          <Canvas stlFile={stl_url} color={color} />
        </div>
      </div>
      <details>
        <summary class="font-medium py-2">add special chars</summary>
        <p class="font-medium">This uses the Roboto font, so some unicode characters are available. Here's a few of them for more convenient copy/paste:</p>
        <p class="font-normal" style="font-family: Roboto;">⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉¼½¾©®™¡¢£¤¥¦§¨ª«¬¯°±´µ¶·¸º»¿×æ÷ʭΔΘεφ҈҉†‡•‣․‥…›※‼‽‾‿⁀⁁⁂⁃⁄⁊⁋⁌⁍⁎⁏⁐⁑⁕⁖⁘⁙⁚⁛⁜⁝⁞√∞∫≈≠≤≥␣◊⸎⸙⸚ꙮ</p>
      </details>
      <div>3D Models Used:</div>
      <div class="font-medium">
        <a style="color: rgb(59 130 246); text-decoration: underline" target="_blank" href="https://www.thingiverse.com/thing:4963377">simple among us model</a>
        <br/>
        <a style="color: rgb(59 130 246); text-decoration: underline" target="_blank" href="https://www.thingiverse.com/thing:2200084">Nike KD8 shoes</a>
        <br/>
        <a style="color: rgb(59 130 246); text-decoration: underline" target="_blank" href="https://www.printables.com/model/77879-among-us-easy-printcrewbodyghostimpostor/files">complex multi-part among us model</a>
    </div>

    </div>

  {:else if state === 'generating'}
    <div class="p-4">
      <div class="font-amogus font-bold text-2xl">
        Generating Preview
      </div>
      <p class="font-medium">This will usually take about 10-20 seconds.</p>
      <img style="width: min(90vw, 500px)" alt="tablet upload task among us" src="/img/among-us-upload.gif" /><br/><br/>
    </div>

  {:else}
    <h1>Error invalid state: {state}. Please reload the page.</h1>

  {/if}
  </div>
</div>
