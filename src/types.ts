// 宠物状态枚举
export type PetState =
  | 'idle' | 'walk' | 'sleep' | 'chase' | 'jump'
  | 'drag' | 'hang' | 'work' | 'hungry' | 'angry'
  | 'eat' | 'play' | 'sick';

// 宠物属性
export interface PetAttributes {
  hunger: number;    // 0-100
  mood: number;      // 0-100
  intimacy: number;  // 0-100
}

// 背包物品
export interface InventoryItem {
  id: string;
  name: string;
  type: 'food' | 'toy' | 'cosmetic';
  price: number;
  effect: { hunger?: number; mood?: number };
  count: number;
}

// 装扮
export interface Equipped {
  hat?: string;
  clothes?: string;
}

// 完整存档
export interface SaveData {
  coins: number;
  inventory: InventoryItem[];
  pet: PetAttributes;
  equipped: Equipped;
  lastSave: number;
}

// 初始存档
export const DEFAULT_SAVE: SaveData = {
  coins: 100,
  inventory: [],
  pet: { hunger: 100, mood: 100, intimacy: 0 },
  equipped: {},
  lastSave: Date.now(),
};

// 商店商品定义
export const SHOP_ITEMS: Omit<InventoryItem, 'count'>[] = [
  { id: 'apple', name: '苹果', type: 'food', price: 5, effect: { hunger: 20 } },
  { id: 'cake', name: '蛋糕', type: 'food', price: 15, effect: { hunger: 40, mood: 5 } },
  { id: 'juice', name: '果汁', type: 'food', price: 10, effect: { hunger: 25 } },
  { id: 'hat', name: '小帽子', type: 'cosmetic', price: 50, effect: {} },
  { id: 'ball', name: '玩具球', type: 'toy', price: 30, effect: { mood: 30 } },
];

// 精灵帧配置
export interface SpriteConfig {
  frameWidth: number;
  frameHeight: number;
  rows: Record<PetState, number>;
  framesPerRow: Record<PetState, number>;
}
