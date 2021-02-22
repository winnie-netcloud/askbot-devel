<script>
  import MainPage from './_components/MainPage.svelte'
  import { gettext } from 'django-i18n'
  // tr: a simple string
  const str = gettext('hello world')
</script>
<MainPage />
