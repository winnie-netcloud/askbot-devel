<script>
  import { goto, metatags } from '@roxi/routify'
  import { fade } from 'svelte/transition'
  metatags.title = 'Register'

  let API_HOST = 'http://localhost.askbot.com:8000'

  function register() {
    console.log(login, email, password)
    fetch(`${API_HOST}/token/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    }).then(data =>
      console.log(data)
    ).then(
      $goto('./index')
    )
  }

  let login = ''
  let password = ''
  let password2 = ''
  let loggedIn = false
  let email = ''
  $: login
  $: email
  $: password
  $: password2

</script>

<style>
  form {
    height: calc(100vh - 2rem);
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
  }
  h1 {
    margin: 0 0 .75rem;
  }
</style>

<form in:fade={{duration: 250}}>
  <h1>Register</h1>
  <input name='login' placeholder='Login' type='text' bind:value={login}  />
  <input name='email' placeholder='Email address' type='email' bind:value={email} />
  <input name='password' placeholder='Password' type='password' bind:value={password} />
  <input name='password2' placeholder='Retype password' type='password' bind:value={password2} />
  <div>
    <input type='submit' value='Register' on:click={register} />
    <input type='reset' value='Clear' />
  </div>
</form>
