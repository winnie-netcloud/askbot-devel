<script>
  import ThreadSummary from './ThreadSummary.svelte'
  export let threads
</script>

<style>
  ul {
    list-style: none;
    padding: 0;
  }
</style>

<ul>
  {#if threads}
    {#each threads as thread}
      <li>
        <ThreadSummary {thread} />
      </li>
    {/each}
  {/if}
</ul>
