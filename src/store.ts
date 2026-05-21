import { SaveData, DEFAULT_SAVE } from './types';

const STORE_KEY = 'desktop-pet-save';

export function loadSave(): SaveData {
  try {
    const raw = localStorage.getItem(STORE_KEY);
    if (!raw) return { ...DEFAULT_SAVE, lastSave: Date.now() };
    const data: SaveData = JSON.parse(raw);

    // 计算离线衰减
    const elapsedHours = (Date.now() - data.lastSave) / (1000 * 60 * 60);
    data.pet.hunger = Math.max(0, data.pet.hunger - elapsedHours * 3);
    data.pet.mood = Math.max(0, data.pet.mood - elapsedHours * 2);
    data.lastSave = Date.now();

    return data;
  } catch {
    return { ...DEFAULT_SAVE, lastSave: Date.now() };
  }
}

export function saveSave(data: SaveData): void {
  data.lastSave = Date.now();
  localStorage.setItem(STORE_KEY, JSON.stringify(data));
}
