<script>
  import Tag from '../../_components/Tag.svelte'
  import TagLink from '../../_components/TagLink.svelte'
  import ThreadSummaryStats from './ThreadSummaryStats.svelte'
  export let thread
  console.log(thread)
</script>

<style>
  .thread-summary {
    display: flex;
    justify-content: space-between;
    flex-wrap: nowrap;
  }
  ul {
    list-style: none;
    padding: 0;
  }
  li {
    display: inline-block;
  }
</style>

<div class='thread-summary'>
  <div>
    <a class='thread-summary__title'>{thread.title}</a>
    {#if thread.tag_names.length }
      <ul class='thread-summary__tags'>
        {#each thread.tag_names as tagName}
          <li>
            <Tag>
              <TagLink {tagName} />
            </Tag>
          </li>
        {/each}
      </ul>
    {/if}
  </div>
  <div>
    <ThreadSummaryStats {thread} />
  </div>
</div>
