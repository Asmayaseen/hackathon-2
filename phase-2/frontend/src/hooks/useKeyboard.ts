/**
 * Keyboard Shortcuts Hook
 *
 * Task: T020
 * Spec: specs/1-phase2-advanced-features/spec.md (US10)
 */
import { useHotkeys } from 'react-hotkeys-hook';

export interface KeyboardCallbacks {
  onNewTask?: () => void;
  onExport?: () => void;
  onImport?: () => void;
  onSearch?: () => void;
  onToggleComplete?: () => void;
  onNavigateDown?: () => void;
  onNavigateUp?: () => void;
  onShowHelp?: () => void;
}

export function useKeyboard(callbacks: KeyboardCallbacks) {
  // Ctrl+E: Export
  useHotkeys('ctrl+e, meta+e', (e) => {
    e.preventDefault();
    callbacks.onExport?.();
  }, { enableOnFormTags: false });

  // Ctrl+I: Import
  useHotkeys('ctrl+i, meta+i', (e) => {
    e.preventDefault();
    callbacks.onImport?.();
  }, { enableOnFormTags: false });

  // n: New task
  useHotkeys('n', () => {
    callbacks.onNewTask?.();
  }, { enableOnFormTags: false });

  // /: Focus search
  useHotkeys('/', (e) => {
    e.preventDefault();
    callbacks.onSearch?.();
  }, { enableOnFormTags: false });

  // x: Toggle complete
  useHotkeys('x', () => {
    callbacks.onToggleComplete?.();
  }, { enableOnFormTags: false });

  // j: Navigate down
  useHotkeys('j', () => {
    callbacks.onNavigateDown?.();
  }, { enableOnFormTags: false });

  // k: Navigate up
  useHotkeys('k', () => {
    callbacks.onNavigateUp?.();
  }, { enableOnFormTags: false });

  // ?: Show help
  useHotkeys('shift+/, ?', (e) => {
    e.preventDefault();
    callbacks.onShowHelp?.();
  }, { enableOnFormTags: false });
}
