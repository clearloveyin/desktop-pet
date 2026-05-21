import { Pet } from './pet';
import { Interaction } from './interaction';
import { Shop } from './shop';
import { saveSave } from './store';

const canvas = document.getElementById('pet-canvas') as HTMLCanvasElement;

// 适配窗口大小
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
window.addEventListener('resize', () => {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
});

// 初始化
const pet = new Pet(canvas);
const shop = new Shop(pet.save);
const interaction = new Interaction(pet, canvas);

// 连接交互回调
interaction.onOpenShop = () => showShopPanel();
interaction.onFeed = () => showFeedPanel();
interaction.onWork = () => {
  pet.startWork();
  interaction.showBubble('开始打工！每分钟赚金币~');
};
interaction.onExit = () => {
  saveSave(pet.save);
  try { (window as any).__TAURI__?.core?.window?.getCurrent?.()?.close?.(); } catch {}
  window.close();
};

function showShopPanel(): void {
  const items = shop.getItems();
  const lines = items.map(i => `${i.name} (${i.price}💰)`).join(' | ');
  interaction.showBubble(`🏪 ${lines} | 余额:${pet.save.coins}💰`);
}

function showFeedPanel(): void {
  const foodItems = shop.getInventory().filter(i => i.type === 'food' && i.count > 0);
  if (foodItems.length === 0) {
    interaction.showBubble('背包中没有食物，先去商店买吧~');
    return;
  }
  const food = foodItems[0];
  const result = shop.use(food.id);
  if (result.success) {
    pet.feed(food.id, result.effect.hunger, result.effect.mood);
    interaction.showBubble(`吃了 ${food.name}！饱食度 +${result.effect.hunger}`);
  }
}

// 主循环
let lastTime = performance.now();
function loop(time: number): void {
  const dt = time - lastTime;
  lastTime = time;
  pet.update(dt);
  interaction.update(dt);
  requestAnimationFrame(loop);
}

// 定时自动保存（每 30 秒）
setInterval(() => saveSave(pet.save), 30000);

// 窗口关闭前保存
window.addEventListener('beforeunload', () => saveSave(pet.save));

// 启动
requestAnimationFrame(loop);
