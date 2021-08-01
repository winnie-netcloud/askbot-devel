<script>
  export let thread
  import Fa from 'fa-svelte'
  import { faCheckCircle } from '@fortawesome/free-solid-svg-icons'
</script>

<style>
  .thread-summary-stats {
    display: flex;
    flex-wrap: nowrap;
    grid-gap: 0.5rem;
  }
  .thread-summary-stats__item {
    align-items: center;
    border: 1px solid #dbdbd4;
    display: flex;
    flex-direction: column;
    height: 3.5rem;
    justify-content: center;
    position: relative;
    width: 3.5rem;
  }
  :global(svg.thread-summary-stats__accepted-answer-icon) {
    color: green;
    height: 0.875rem !important;
    position: absolute;
    right: 0.25rem;
    top: 0.25rem;
    vertical-align: top;
    width: 0.875rem !important;
  }
  .thread-summary-stats__item-name {
    font-size: 0.75rem;
  }
  .thread-summary-stats__answers.thread-summary-stats__answers--accepted {
  }
  .thread-summary-stats__count {
    font-size: 1.125rem;
    font-weight: bold;
  }
</style>

<div class='thread-summary-stats'>
  <div class='thread-summary-stats__item thread-summary-stats__votes'>
    <div class='thread-summary-stats__count'>
      {thread.vote_count}
    </div>
    <div class='thread-summary-stats__item-name'>
      {gettext('votes')}
    </div>
  </div>
  <div class={`thread-summary-stats__item
              thread-summary-stats__answers
              ${thread.accepted_answer ? '' : 'thread-summary-stats__answers--accepted'}`}
  >
    <div class='thread-summary-stats__count'>
      <Fa class='thread-summary-stats__accepted-answer-icon' icon={faCheckCircle} />
      {thread.answer_count}
    </div>
    <div class='thread-summary-stats__item-name'>
      {gettext('answers')}
    </div>
  </div>
  <div class='thread-summary-stats__item thread-summary-stats__views'>
    <div class='thread-summary-stats__count'>
      {thread.view_count}
    </div>
    <div class='thread-summary-stats__item-name'>
      {gettext('views')}
    </div>
  </div>
</div>
