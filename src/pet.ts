import { PetState, SaveData } from './types';
import { Renderer } from './renderer';
import { loadSave } from './store';

export class Pet {
  state: PetState = 'idle';
  renderer: Renderer;
  save: SaveData;

  private x: number;
  private y: number;
  private vx = 0;
  private vy = 0;
  private stateTimer = 0;
  private stateDuration = 0;
  private facingRight = true;
  private lastHungerCheck = 0;
  private canvas: HTMLCanvasElement;

  // 打工
  private workTimer = 0;
  private coinsEarnedThisSession = 0;

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas;
    this.renderer = new Renderer(canvas);
    this.x = canvas.width / 2;
    this.y = canvas.height / 2;
    this.save = loadSave();

    // 检查是否长期饥饿
    if (this.save.pet.hunger <= 0) {
      const elapsed = (Date.now() - this.save.lastSave) / (1000 * 60 * 60);
      if (elapsed > 48) {
        this.state = 'sick';
      } else {
        this.state = 'hungry';
      }
    }
  }

  /** 每帧更新 */
  update(dt: number): void {
    this.stateTimer += dt;

    // 每 10 秒检查一次饥饿/心情状态
    this.lastHungerCheck += dt;
    if (this.lastHungerCheck > 10000) {
      this.lastHungerCheck = 0;
      this.decayAttributes();
    }

    // 行走物理
    this.x += this.vx * (dt / 1000);
    this.y += this.vy * (dt / 1000);
    this.clampPosition();

    // 状态超时切换
    if (this.stateTimer >= this.stateDuration && this.stateDuration > 0) {
      this.transitionFrom(this.state);
    }

    // 打工计时
    if (this.state === 'work') {
      this.workTimer += dt;
      if (this.workTimer >= 60000) {
        const earned = 2 + Math.floor(Math.random() * 4);
        this.save.coins += earned;
        this.coinsEarnedThisSession += earned;
        this.workTimer = 0;
      }
    }

    this.renderer.setFacingRight(this.facingRight);
    this.renderer.render(this.state, dt);
  }

  /** 状态切换入口 */
  setState(newState: PetState, duration?: number): void {
    this.state = newState;
    this.stateTimer = 0;
    this.stateDuration = duration ?? 0;
    this.vx = 0;
    this.vy = 0;
  }

  /** 自动过渡逻辑 */
  private transitionFrom(state: PetState): void {
    switch (state) {
      case 'walk':
        this.setState('idle', 3000 + Math.random() * 5000);
        break;
      case 'jump':
        this.setState('idle', 3000 + Math.random() * 5000);
        break;
      case 'eat':
      case 'play':
        this.setState('idle', 3000 + Math.random() * 5000);
        break;
      case 'idle':
        if (Math.random() < 0.3) {
          this.startWalk();
        } else if (Math.random() < 0.15) {
          this.setState('sleep', 8000 + Math.random() * 10000);
        } else {
          this.setState('idle', 3000 + Math.random() * 5000);
        }
        break;
      case 'sleep':
        this.setState('idle', 3000 + Math.random() * 5000);
        break;
      default:
        this.setState('idle', 3000 + Math.random() * 5000);
    }
  }

  /** 开始随机行走 */
  private startWalk(): void {
    const angle = Math.random() * Math.PI * 2;
    const speed = 30 + Math.random() * 50;
    this.vx = Math.cos(angle) * speed;
    this.vy = Math.sin(angle) * speed;
    this.facingRight = this.vx >= 0;
    this.setState('walk', 2000 + Math.random() * 3000);
  }

  /** 限制宠物在窗口内 */
  private clampPosition(): void {
    const margin = 40;
    if (this.x < margin) { this.x = margin; this.vx = Math.abs(this.vx); this.facingRight = true; }
    if (this.x > this.canvas.width - margin) { this.x = this.canvas.width - margin; this.vx = -Math.abs(this.vx); this.facingRight = false; }
    if (this.y < margin) { this.y = margin; this.vy = Math.abs(this.vy); }
    if (this.y > this.canvas.height - margin) { this.y = this.canvas.height - margin; this.vy = -Math.abs(this.vy); }

    if (this.x <= margin || this.x >= this.canvas.width - margin) {
      if (this.state === 'walk') this.setState('idle', 2000);
    }
    if (this.y <= margin || this.y >= this.canvas.height - margin) {
      if (this.state === 'walk') this.setState('idle', 2000);
    }
  }

  /** 属性自然衰减 */
  private decayAttributes(): void {
    const p = this.save.pet;
    p.hunger = Math.max(0, p.hunger - 0.05);
    p.mood = Math.max(0, p.mood - 0.033);

    if (p.hunger < 30 && this.state !== 'eat' && this.state !== 'drag') {
      if (this.state !== 'hungry') this.setState('hungry');
    }
    if (p.mood < 20 && this.state !== 'play' && this.state !== 'drag') {
      if (this.state !== 'angry') this.setState('angry');
    }
    if (p.hunger >= 30 && this.state === 'hungry') {
      this.setState('idle', 3000);
    }
    if (p.mood >= 20 && this.state === 'angry') {
      this.setState('idle', 3000);
    }
  }

  // ─── 交互接口（由 interaction.ts 调用）───

  onClick(): void {
    if (this.state === 'angry') return;
    this.setState('jump', 600);
    this.save.pet.intimacy = Math.min(100, this.save.pet.intimacy + 1);
  }

  onDoubleClick(): void {
    if (this.state === 'angry') return;
    this.setState('jump', 800);
    this.save.pet.intimacy = Math.min(100, this.save.pet.intimacy + 1);
  }

  onDragStart(): void {
    this.setState('drag');
  }

  onDragEnd(x: number, y: number): void {
    this.x = x;
    this.y = y;
    if (x < 30 || x > this.canvas.width - 30 || y < 30 || y > this.canvas.height - 30) {
      this.setState('hang', 5000);
    } else {
      this.setState('idle', 2000);
    }
  }

  onMouseNear(dist: number, mouseX: number): void {
    if (this.state === 'drag' || this.state === 'sleep') return;
    if (dist < 20 && this.state !== 'chase') {
      this.setState('chase');
    } else if (dist >= 20 && this.state === 'chase') {
      this.setState('idle', 2000);
    }
    this.facingRight = mouseX > this.x;
  }

  startWork(): void {
    if (this.state === 'drag') return;
    this.setState('work', 300000);
    this.workTimer = 0;
    this.coinsEarnedThisSession = 0;
  }

  stopWork(): number {
    if (this.state === 'work') {
      this.setState('idle', 2000);
    }
    return this.coinsEarnedThisSession;
  }

  feed(foodId: string, hungerRestore: number, moodRestore: number): void {
    if (this.state === 'drag') return;
    this.setState('eat', 2000);
    this.save.pet.hunger = Math.min(100, this.save.pet.hunger + hungerRestore);
    this.save.pet.mood = Math.min(100, this.save.pet.mood + moodRestore);
    this.save.pet.intimacy = Math.min(100, this.save.pet.intimacy + 3);
    if (this.state === 'hungry' && this.save.pet.hunger >= 30) {
      this.setState('idle', 2000);
    }
  }

  playWith(moodRestore: number): void {
    if (this.state === 'drag') return;
    this.setState('play', 3000);
    this.save.pet.mood = Math.min(100, this.save.pet.mood + moodRestore);
    this.save.pet.intimacy = Math.min(100, this.save.pet.intimacy + 3);
    if (this.state === 'angry' && this.save.pet.mood >= 20) {
      this.setState('idle', 2000);
    }
  }

  getPosition(): { x: number; y: number } {
    return { x: this.x, y: this.y };
  }

  getSpeechBubble(): string {
    const intimacy = this.save.pet.intimacy;
    switch (this.state) {
      case 'hungry': return '好饿...' + (Math.random() < 0.5 ? ' 🍔' : '');
      case 'angry': return Math.random() < 0.5 ? '哼！' : '别碰我！';
      case 'work': return Math.random() < 0.5 ? '打工中...' : '赚钱买好吃的！';
      case 'sleep': return 'Zzz...';
      case 'eat': return '好好吃~';
      case 'play': return '好好玩！';
      case 'sick': return '好难受...';
      case 'idle':
        if (intimacy < 10) return Math.random() < 0.5 ? '你是谁？' : '...';
        if (intimacy > 60) return Math.random() < 0.5 ? '最喜欢主人了！❤️' : '主人~';
        return Math.random() < 0.5 ? '主人~' : '好无聊...';
      default: return '';
    }
  }
}
