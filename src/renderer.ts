import { PetState, SpriteConfig } from './types';

export class Renderer {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private sprite: HTMLImageElement | null = null;
  private spriteConfig: SpriteConfig | null = null;
  private currentFrame = 0;
  private frameTimer = 0;
  private facingRight = true;

  static readonly PET_WIDTH = 128;
  static readonly PET_HEIGHT = 128;

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d')!;
  }

  /** 加载精灵图（可选，无素材时用程序化绘制） */
  loadSprite(image: HTMLImageElement, config: SpriteConfig): void {
    this.sprite = image;
    this.spriteConfig = config;
  }

  /** 每帧调用，状态 + dt 推进帧动画 */
  render(state: PetState, dt: number): void {
    this.frameTimer += dt;
    const fps = 8;
    if (this.frameTimer > 1000 / fps) {
      this.frameTimer = 0;
      this.currentFrame++;
    }

    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    if (this.sprite && this.spriteConfig) {
      this.renderSprite(state);
    } else {
      this.renderProcedural(state);
    }
  }

  /** 精灵图渲染 */
  private renderSprite(state: PetState): void {
    const cfg = this.spriteConfig!;
    const row = cfg.rows[state];
    const frameCount = cfg.framesPerRow[state];
    const frame = this.currentFrame % Math.max(frameCount, 1);
    const { frameWidth, frameHeight } = cfg;

    const sx = frame * frameWidth;
    const sy = row * frameHeight;

    this.ctx.save();
    if (!this.facingRight) {
      this.ctx.translate(this.canvas.width, 0);
      this.ctx.scale(-1, 1);
      this.ctx.drawImage(
        this.sprite!, sx, sy, frameWidth, frameHeight,
        this.canvas.width - frameWidth - 0, 0, frameWidth, frameHeight
      );
    } else {
      this.ctx.drawImage(
        this.sprite!, sx, sy, frameWidth, frameHeight,
        0, 0, frameWidth, frameHeight
      );
    }
    this.ctx.restore();
  }

  /** 程序化绘制（无素材时的后备方案） */
  private renderProcedural(state: PetState): void {
    const w = this.canvas.width;
    const h = this.canvas.height;
    const cx = w / 2;
    const cy = h / 2;
    const bounce = Math.sin(this.currentFrame * 0.5) * 3;

    this.ctx.save();
    if (!this.facingRight) {
      this.ctx.translate(w, 0);
      this.ctx.scale(-1, 1);
    }

    // 身体
    this.ctx.fillStyle = '#ffccaa';
    this.ctx.beginPath();
    if (state === 'sleep') {
      this.ctx.ellipse(cx, cy + 10, 40, 28, 0, 0, Math.PI * 2);
    } else if (state === 'jump') {
      this.ctx.ellipse(cx, cy + bounce - 5, 35, 45, 0, 0, Math.PI * 2);
    } else {
      this.ctx.ellipse(cx, cy + bounce, 38, 38, 0, 0, Math.PI * 2);
    }
    this.ctx.fill();

    // 眼睛
    this.ctx.fillStyle = '#333';
    if (state === 'sleep') {
      this.ctx.lineWidth = 2;
      this.ctx.beginPath();
      this.ctx.arc(cx - 12, cy + 5, 6, 0, Math.PI);
      this.ctx.stroke();
      this.ctx.beginPath();
      this.ctx.arc(cx + 12, cy + 5, 6, 0, Math.PI);
      this.ctx.stroke();
    } else if (state === 'angry') {
      this.ctx.lineWidth = 2;
      this.ctx.beginPath();
      this.ctx.moveTo(cx - 18, cy - 3);
      this.ctx.lineTo(cx - 8, cy - 10);
      this.ctx.lineTo(cx - 2, cy - 3);
      this.ctx.stroke();
      this.ctx.beginPath();
      this.ctx.moveTo(cx + 18, cy - 3);
      this.ctx.lineTo(cx + 8, cy - 10);
      this.ctx.lineTo(cx + 2, cy - 3);
      this.ctx.stroke();
    } else {
      this.ctx.beginPath();
      this.ctx.arc(cx - 12, cy - 5, 6, 0, Math.PI * 2);
      this.ctx.fill();
      this.ctx.beginPath();
      this.ctx.arc(cx + 12, cy - 5, 6, 0, Math.PI * 2);
      this.ctx.fill();
      this.ctx.fillStyle = '#fff';
      this.ctx.beginPath();
      this.ctx.arc(cx - 10, cy - 7, 2, 0, Math.PI * 2);
      this.ctx.fill();
      this.ctx.beginPath();
      this.ctx.arc(cx + 14, cy - 7, 2, 0, Math.PI * 2);
      this.ctx.fill();
    }

    // 嘴巴
    this.ctx.fillStyle = '#e88';
    if (state === 'angry') {
      this.ctx.beginPath();
      this.ctx.arc(cx, cy + 15, 5, 0, Math.PI, true);
      this.ctx.fill();
    } else if (state === 'hungry') {
      this.ctx.beginPath();
      this.ctx.ellipse(cx, cy + 12, 5, 7, 0, 0, Math.PI * 2);
      this.ctx.fill();
    } else if (state === 'work') {
      this.ctx.lineWidth = 1.5;
      this.ctx.beginPath();
      this.ctx.moveTo(cx - 6, cy + 12);
      this.ctx.lineTo(cx + 6, cy + 12);
      this.ctx.stroke();
    } else {
      this.ctx.beginPath();
      this.ctx.arc(cx, cy + 5, 8, 0.2, Math.PI - 0.2);
      this.ctx.fill();
    }

    // 腮红
    this.ctx.fillStyle = 'rgba(255,150,150,0.3)';
    this.ctx.beginPath();
    this.ctx.ellipse(cx - 22, cy + 8, 8, 5, 0, 0, Math.PI * 2);
    this.ctx.fill();
    this.ctx.beginPath();
    this.ctx.ellipse(cx + 22, cy + 8, 8, 5, 0, 0, Math.PI * 2);
    this.ctx.fill();

    // 打工状态 — 安全帽
    if (state === 'work') {
      this.ctx.fillStyle = '#ffd700';
      this.ctx.beginPath();
      this.ctx.arc(cx, cy - 38, 28, Math.PI, 0);
      this.ctx.fill();
      this.ctx.fillStyle = '#ffaa00';
      this.ctx.fillRect(cx - 20, cy - 42, 40, 6);
    }

    // 饥饿 — 汗滴
    if (state === 'hungry') {
      this.ctx.fillStyle = '#6cf';
      this.ctx.beginPath();
      const dropY = cy - 42 + Math.sin(this.currentFrame * 0.8) * 4;
      this.ctx.ellipse(cx + 30, dropY, 3, 5, 0.2, 0, Math.PI * 2);
      this.ctx.fill();
    }

    // 睡觉 — ZZz
    if (state === 'sleep') {
      this.ctx.fillStyle = '#888';
      this.ctx.font = '14px sans-serif';
      const zPhase = this.currentFrame % 3;
      if (zPhase >= 0) this.ctx.fillText('z', cx + 25, cy - 25);
      if (zPhase >= 1) this.ctx.fillText('z', cx + 35, cy - 35);
      if (zPhase >= 2) this.ctx.fillText('Z', cx + 45, cy - 45);
    }

    this.ctx.restore();
  }

  setFacingRight(right: boolean): void {
    this.facingRight = right;
  }

  resize(width: number, height: number): void {
    this.canvas.width = width;
    this.canvas.height = height;
  }
}
