import { Pet } from './pet';

export class Interaction {
  private pet: Pet;
  private canvas: HTMLCanvasElement;
  private bubble: HTMLElement;
  private menu: HTMLElement;
  private dragging = false;
  private dragOffsetX = 0;
  private dragOffsetY = 0;
  private bubbleTimer = 0;
  private lastMouseX = 0;

  // 回调
  onOpenShop?: () => void;
  onFeed?: () => void;
  onWork?: () => void;
  onExit?: () => void;

  constructor(pet: Pet, canvas: HTMLCanvasElement) {
    this.pet = pet;
    this.canvas = canvas;
    this.bubble = document.getElementById('speech-bubble')!;
    this.menu = document.getElementById('context-menu')!;

    this.bindEvents();
  }

  private bindEvents(): void {
    // 鼠标按下
    this.canvas.addEventListener('mousedown', (e) => {
      this.hideMenu();
      if (e.button === 0) {
        const pos = this.pet.getPosition();
        const dist = Math.hypot(e.offsetX - pos.x, e.offsetY - pos.y);
        if (dist < 50) {
          this.dragging = true;
          this.dragOffsetX = pos.x - e.offsetX;
          this.dragOffsetY = pos.y - e.offsetY;
          this.pet.onDragStart();
        }
      }
    });

    // 鼠标移动
    this.canvas.addEventListener('mousemove', (e) => {
      this.lastMouseX = e.offsetX;
      if (this.dragging) {
        this.pet.onDragEnd(e.offsetX + this.dragOffsetX, e.offsetY + this.dragOffsetY);
        this.pet.onDragStart();
      } else {
        const pos = this.pet.getPosition();
        const dist = Math.hypot(e.offsetX - pos.x, e.offsetY - pos.y);
        this.pet.onMouseNear(dist, e.offsetX);
      }
    });

    // 鼠标松开
    this.canvas.addEventListener('mouseup', (e) => {
      if (this.dragging) {
        this.dragging = false;
        this.pet.onDragEnd(e.offsetX + this.dragOffsetX, e.offsetY + this.dragOffsetY);
        return;
      }
      if (e.button === 0) {
        const pos = this.pet.getPosition();
        const dist = Math.hypot(e.offsetX - pos.x, e.offsetY - pos.y);
        if (dist < 50) {
          const now = Date.now();
          const lastClick = (this.canvas as any).__lastClick || 0;
          if (now - lastClick < 400) {
            this.pet.onDoubleClick();
            this.showBubble('❤️');
          } else {
            this.pet.onClick();
            this.showBubble(this.pet.getSpeechBubble());
          }
          (this.canvas as any).__lastClick = now;
        }
      }
    });

    // 右键菜单
    this.canvas.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      const pos = this.pet.getPosition();
      const dist = Math.hypot(e.offsetX - pos.x, e.offsetY - pos.y);
      if (dist < 60) {
        this.menu.style.left = e.offsetX + 'px';
        this.menu.style.top = e.offsetY + 'px';
        this.menu.style.display = 'block';
      }
    });

    // 菜单项点击
    this.menu.addEventListener('click', (e) => {
      const target = e.target as HTMLElement;
      const action = target.dataset.action;
      this.hideMenu();
      switch (action) {
        case 'feed': this.onFeed?.(); break;
        case 'shop': this.onOpenShop?.(); break;
        case 'work': this.onWork?.(); break;
        case 'status': this.showStatusDialog(); break;
        case 'exit': this.onExit?.(); break;
      }
    });

    // 点击菜单外关闭
    document.addEventListener('click', () => this.hideMenu());
  }

  /** 显示对话气泡 */
  showBubble(text: string): void {
    if (!text) return;
    this.bubble.textContent = text;
    this.bubble.style.display = 'block';
    const pos = this.pet.getPosition();
    this.bubble.style.left = (pos.x - 30) + 'px';
    this.bubble.style.top = (pos.y - 60) + 'px';
    this.bubbleTimer = 2000;
  }

  /** 更新气泡位置和计时 */
  update(dt: number): void {
    if (this.bubbleTimer > 0) {
      this.bubbleTimer -= dt;
      if (this.bubbleTimer <= 0) {
        this.bubble.style.display = 'none';
      }
      const pos = this.pet.getPosition();
      this.bubble.style.left = (pos.x - 30) + 'px';
      this.bubble.style.top = (pos.y - 60) + 'px';
    }
  }

  private hideMenu(): void {
    this.menu.style.display = 'none';
  }

  private showStatusDialog(): void {
    const p = this.pet.save.pet;
    const msg = `饱食度: ${Math.round(p.hunger)}/100 | 心情: ${Math.round(p.mood)}/100 | 亲密度: ${Math.round(p.intimacy)}/100 | 金币: ${this.pet.save.coins}`;
    this.showBubble(msg);
  }
}
