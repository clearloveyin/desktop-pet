import { SaveData, SHOP_ITEMS, InventoryItem } from './types';
import { saveSave } from './store';

export class Shop {
  save: SaveData;

  constructor(save: SaveData) {
    this.save = save;
  }

  /** 获取商店商品列表 */
  getItems(): Omit<InventoryItem, 'count'>[] {
    return SHOP_ITEMS;
  }

  /** 购买商品 */
  buy(itemId: string): { success: boolean; message: string; item?: InventoryItem } {
    const def = SHOP_ITEMS.find(i => i.id === itemId);
    if (!def) return { success: false, message: '商品不存在' };

    if (this.save.coins < def.price) {
      return { success: false, message: '金币不足！' };
    }

    this.save.coins -= def.price;

    const existing = this.save.inventory.find(i => i.id === itemId);
    if (existing) {
      existing.count++;
    } else {
      this.save.inventory.push({ ...def, count: 1 });
    }

    saveSave(this.save);
    return { success: true, message: `购买了 ${def.name}！`, item: { ...def, count: 1 } };
  }

  /** 使用物品（喂食或玩耍） */
  use(itemId: string): { success: boolean; message: string; effect: { hunger: number; mood: number } } {
    const item = this.save.inventory.find(i => i.id === itemId && i.count > 0);
    if (!item) return { success: false, message: '背包中没有该物品', effect: { hunger: 0, mood: 0 } };

    item.count--;
    if (item.count <= 0) {
      this.save.inventory = this.save.inventory.filter(i => i.id !== itemId);
    }

    saveSave(this.save);
    return {
      success: true,
      message: `使用了 ${item.name}！`,
      effect: { hunger: item.effect.hunger || 0, mood: item.effect.mood || 0 },
    };
  }

  /** 装备装扮 */
  equip(itemId: string): { success: boolean; message: string } {
    const item = SHOP_ITEMS.find(i => i.id === itemId && i.type === 'cosmetic');
    if (!item) return { success: false, message: '该物品不是装扮' };

    const existing = this.save.inventory.find(i => i.id === itemId && i.count > 0);
    if (!existing) return { success: false, message: '背包中没有该装扮' };

    if (itemId === 'hat') {
      this.save.equipped.hat = this.save.equipped.hat === 'hat' ? undefined : 'hat';
      saveSave(this.save);
      return { success: true, message: this.save.equipped.hat ? '戴上了小帽子！' : '摘下了小帽子！' };
    }

    return { success: false, message: '未知装扮' };
  }

  /** 获取背包 */
  getInventory(): InventoryItem[] {
    return this.save.inventory;
  }
}
