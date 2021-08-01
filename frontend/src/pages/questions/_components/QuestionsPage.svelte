<script>
  import { params, page, ready, redirect, url } from '@roxi/routify'
  import { API_BASE_URL } from '../../../config'
  import { getCanonicalUrl, getSearchParams } from '../_lib/urlUtils'
  import { onMount } from 'svelte'
  import Headline from './Headline.svelte'
  import Contributors from './Contributors.svelte'
  import TabBar from './TabBar.svelte'
  import TagSearch from './TagSearch.svelte'
  import SearchTags from './SearchTags.svelte'
  import TagSelector from './TagSelector.svelte'
  import RelatedTags from './RelatedTags.svelte'
  import DisplaySettingAsHtml from '../../_components/DisplaySettingAsHtml.svelte'
  import Paginator from '../../_components/Paginator.svelte'
  import Threads from './Threads.svelte'

  $: searchParams = getSearchParams($params)

  let data = {}
  let apiLoaded = false

  fetch(`${API_BASE_URL}/question-search/?format=json`)
    .then(response => response.json())
    .then(json => {data = json})
    .then($ready)
    .catch(error => console.log(error))

  // Redirect to the canonical url
  onMount(() => {
    const canonical = getCanonicalUrl(searchParams)
    if ($url() !== canonical) {
      $redirect(canonical)
    }
  })

</script>

<main>
  <div class="q-list-header">
    <Headline count={data.num_threads} />
    <TabBar {data} />
    <SearchTags tags={searchParams.tags} />
  </div>
  <Threads threads={data.threads} />
  <Paginator
    numPages={data.num_pages}
    page={data.page}
    urlParams={searchParams}
    urlBuilder={getCanonicalUrl}
  />
</main>
<aside>
  <DisplaySettingAsHtml setting='SIDEBAR_MAIN_HEADER' />
  <Contributors contributors={data.contributors} />
  <TagSearch />
  <TagSelector />
  <RelatedTags />
  <DisplaySettingAsHtml setting='SIDEBAR_MAIN_FOOTER' />
</aside>
