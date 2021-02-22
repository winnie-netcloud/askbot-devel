<script>
  import { goto, metatags } from '@roxi/routify'
  import { fade } from 'svelte/transition'
  import userStore from '../stores/userStore.js'

  metatags.title = 'Log in'

  let API_HOST = 'http://localhost.askbot.com:8000'

  function authenticate(evt) {
    evt.preventDefault()
    fetch(`${API_HOST}/token/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            username: login,
            password: password
        })
    }).then(data => data.json()
    ).then(json => {
      const data = {
        token: json.token,
        email: json.user.email,
        userName: json.user.username,
        id: json.user.id
      }
      userStore.set(data)
      userStore.save()
      $goto('./index')
    }).catch(error => console.log(error))
  }

  let login = ''
  let password = ''
  let loggedIn = false
  $: login
  $: password
  $: loggedIn

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
  <h1>{gettext('Login')}</h1>
  <input name='login' placeholder={gettext('Login name or email')} type='text' bind:value={login}  />
  <input name='password' placeholder={gettext('Password')} type='password' bind:value={password} />
  <div>
    <input type='submit' value={gettext('Login')} on:click={authenticate} />
    <input type='reset' value={gettext('Clear')} />
  </div>
</form>
