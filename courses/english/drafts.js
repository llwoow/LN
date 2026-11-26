'use strict';
// 英语微课开放题草稿只在本机保存。不会上传用户答案或成绩。
(() => {
  const prefix = 'ln.english.draft.v1.';
  function restore() {
    document.querySelectorAll('textarea[data-ln-english-draft]:not([data-ln-draft-ready])').forEach((area) => {
      area.dataset.lnDraftReady = '1';
      try { area.value = localStorage.getItem(prefix + area.dataset.lnEnglishDraft) ?? ''; }
      catch { area.title = '当前浏览器不支持草稿持久保存'; }
    });
  }
  document.addEventListener('input', (event) => {
    const target = event.target;
    if (!(target instanceof HTMLTextAreaElement) || !target.matches('[data-ln-english-draft]')) return;
    try { localStorage.setItem(prefix + target.dataset.lnEnglishDraft, target.value); }
    catch { target.title = '草稿无法保存在当前浏览器'; }
  });
  document.addEventListener('DOMContentLoaded', () => {
    const main = document.getElementById('main');
    if (main) new MutationObserver(restore).observe(main, {childList: true, subtree: true});
    restore();
  });
})();
