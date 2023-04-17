<svelte:head>
  <title>eV 7393's amogus emporium!</title>
	<link rel='icon' type='image/png' href='/favicon.png'>
</svelte:head>

<script>
  import Canvas from "../src/lib/Canvas.svelte";
  // import "./app.css";

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
  let submit_button_disabled = true;
  let submit_button_text = 'Submit';
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

    submit_button_disabled = status === 'submitted';
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
    } else if (status === 'generated') {
      state = 'review';
    } else if (status === 'submitted') {
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
          } else if (status === 'submitted') {
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
      submit_button_disabled = true;
      submit_button_text = 'submitting...';
      fetch('/submit').then(res => res.text()).then(res => {
        if (res === 'already submitted') {
          submit_button_disabled = true;
          submit_button_text = 'submitted';
          alert('You already submitted a model, you may not change it after.');
          state = 'waiting';
        } else if (res === 'queue full') {
          submit_button_disabled = false;
          submit_button_text = 'submit';
          alert("The print queue is full. Try again tomorrow, or stop by FTC 7393's pit to pick up a non-custom figurine.");
          state = 'customize';
        } else {
          submit_button_disabled = true;
          submit_button_text = 'submitted';
          alert('Submitted successfully. Keep this page open, you will receive an alert when the print is ready to pick up. If you entered your phone number, you will also receive a text.');
          state = 'waiting';
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
        printed = json.printed;
        taken = json.taken;
        if (printed && (!taken || !have_alerted_for_print_done)) {
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

<a href="/logout">logout</a> &nbsp; &nbsp; &nbsp; <a href="https://ftc7393.org">ftc7393.org</a> &nbsp; &nbsp; &nbsp; <a target="_blank" href="https://github.com/fTC7393/sussy-factory">source code</a><br/>

{#if state === 'loading'}
<h1>Loading...</h1>

{:else if state === 'info'}
<h1>Enter Your Info</h1>
<label>team/name (e.g. FTC 7393 or Joe Schmoe): <input type="text" id="team" name="team" bind:value="{team}" /></label><br/>
<label>(optional) phone number to be notified when the print is done (SMS charges may apply): <input type="text" id="phone" name="phone" bind:value="{phone}" /></label><br/>
<button on:click={save_info}>next</button>

{:else if state === 'customize'}
<br/>
<button on:click={edit_info}>edit team info</button>
<h1>Customize Your Figurine</h1>
<label>top text: <input type="text" id="top_text" name="top_text" bind:value={top_text} /></label><br/>
<label>bottom text (optional): <input type="text" id="bottom_text" name="bottom_text" bind:value={bottom_text} /></label><br/>
<label>shoes?<input type="checkbox" id="shoes" name="shoes" bind:checked={shoes}></label><br/>
<button on:click={generate}>customize</button>
<p>If no bottom text is provided, the top text will be moved to the middle.</p>
<p style="font-weight: bold">NOTE: Any more than 6 characters on a row will likely be unreadable!</p>
<details>
  <summary>special chars</summary>
<p>This uses the Roboto font, so some unicode characters are available. Here's a few of them for more convenient copy/paste:</p>
<p style="font-family: Roboto;">⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉¼½¾©®™¡¢£¤¥¦§¨ª«¬¯°±´µ¶·¸º»¿×æ÷ʭΔΘεφ҈҉†‡•‣․‥…›※‼‽‾‿⁀⁁⁂⁃⁄⁊⁋⁌⁍⁎⁏⁐⁑⁕⁖⁘⁙⁚⁛⁜⁝⁞√∞∫≈≠≤≥␣◊⸎⸙⸚ꙮ</p>
</details>
<p>color of the day: <span style:background={color_of_the_day_hex}>{color_of_the_day_hex} <span style="color: white">{color_of_the_day_hex}</span></span></p>
<br/>
<Canvas stlFile={stl_url} color={color_of_the_day} />

{:else if state === 'generating'}
<h1>Generating 3D Preview...</h1>
<p>This will usually take about 10-20 seconds.</p>

{:else if state === 'review'}
<h1>Review Your Figurine</h1>
<button on:click={customize}>edit</button>
<button on:click={submit}>submit</button>
<p>Review the figurine and confirm you want to submit it to be 3D printed. You cannot make any changes after submitting.</p>
<p>spots left in print queue: {queue_spots_left}</p>
<br/>
<Canvas stlFile={stl_url} color={color_of_the_day} />

{:else if state === 'waiting'}
<h1>Waiting for Figurine to be Printed</h1>
This page will send an alert once your figurine is printed.
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
error

{/if}
