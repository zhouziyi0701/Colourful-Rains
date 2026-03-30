import pygame
import random
import math
import array

#全局常量与参数初始化
WIDTH, HEIGHT = 1000, 700 #屏幕的大小
FPS = 60 #刷新的帧率

# 状态常量
MENU = 0
GAME = 1
INFO = 2

#频率定义(哆来咪发唆啦西)
FREQ = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88]

#可以外部进行控制的参数
number_setting = {
    "density": 0.2,  # 雨滴密度 (0.1 - 2.0)
    "fade_speed": 10,  # 雨滴消失速度
    "max_ripple": 60,  # 最大水圈大小
    "wind_mag": 3,  # 风力强度
}

# 生成水滴的声音
def generate_water_plink(freq,duration=0.15):
    sample_rate = 44100
    n_samples = int(sample_rate*duration)
    buf = array.array('h',[0]*n_samples) #设置数组，用于存储生成的声音
    for i in range(n_samples):
        t = float(i)/sample_rate #让声音从大变小的函数
        envelope = math.exp(-6.0*i/(sample_rate*0.1)) #速降函数
        v = int(envelope*16384*(math.sin(2.0*math.pi*freq*t)+0.2*math.sin(4.0*math.pi*freq*t)))
        # 应用包络函数并且缩放整个函数到16位音频的量化范围
        buf[i] = v
    return pygame.mixer.Sound(buf)

#导入荷叶以及乌云的图片
Lotus = pygame.image.load('F:/Python_programme/colourful_rains/image/lotus.svg')
Cloud = pygame.image.load('F:/Python_programme/colourful_rains/image/cloud.png')

#生成会移动的乌云
class Black_Cloud:
    # 构造函数。决定这朵云是在游戏刚开始时生成的，还是中途生成使得云朵有运动的效果的。
    def __init__(self,is_initial=False):
        #随机生成乌云的图片大小，随机生成宽和高
        size_w = random.randint(200,400)
        size_h = int(size_w*0.5)
        self.image = pygame.transform.smoothscale(Cloud,(size_w,size_h))

        if is_initial:#游戏初始化阶段，随机将云摆放在屏幕可见范围内的任意水平位置
            self.x = random.randint(-200,WIDTH)
        else:
        #如果是在游戏过程中新生成的云，假设50%概率出现在屏幕左侧外，50%概率出现在屏幕右侧外
            self.x = -400 if random.random()>0.5 else WIDTH+100

        self.y = random.randint(-50,120) #随机设置云位置的高度
        self.speed_factor = random.uniform(0.3,0.6)#随机生成一个速度因子，让不同的云移动速度有快有慢

    # 更新云的状态：接收当前的风力wind_x作为参数，风速变化进而导致云的速度发生变化
    def update(self,wind_x):
        base_drift=0.5 if wind_x >= 0 else -0.5
            #设置基本的移动数据，使得风力为0，云也会移动
        self.x += base_drift+wind_x*self.speed_factor
            #计算最终云的位置，总的位移=基础数据+(风力大小×速度变化因子)
        if self.x > WIDTH+200: self.x=-400
        if self.x < -400: self.x = WIDTH+200
        #如果乌云超出了右边界，将其重置到左侧远处；如果乌云超出了左边界，将其重置到右侧远处
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y)) #将乌云图片放到坐标的位置

#生成荷叶，并且荷叶会随着风的大小的变化进行变化
class LotusLeaf:
    #构建荷叶的坐标位置
    def __init__(self,x,y,rw,rh):
        #，假设荷叶的图片中心坐标为(x, y)和荷叶随风振动的半长宽为(rw, rh)
        self.base_x,self.base_y,self.rw,self.rh = x,y,rw,rh
        #记录下荷叶在水面静止时的位置，假设为原点
        self.phase = random.uniform(0,math.pi*2)
        #随机初始化一个相位角，从0度到360度随机选取，防止所有荷叶同步摆动
        self.shake = 0 #瞬时震动偏移量，用于存储水滴滴落到荷叶上时产生的震动
        self.current_offset = 0 #记录当前状态下，荷叶因波动产生的垂直位移
        self.image = pygame.transform.smoothscale(Lotus,(int(rw*2),int(rh*2)))
        #将荷叶放入初始时定义的位置
    def update(self,wind_mag): #更新每一帧荷叶的位置
        self.phase += 0.05+abs(wind_mag)*0.01
        #用于更新相位。风力wind_mag越大，相位变化越快，振动频率越高。
        self.current_offset = math.sin(self.phase)*(2+abs(wind_mag)) #该公式用于计算位移
        if self.shake>0: #在发生震动之后，调用该函数使得震动衰减，通过缩小shake值，直到该值趋近于0。
            self.shake *= 0.8
    #绘制荷叶
    def draw(self, screen):
        draw_x = self.base_x-self.rw #计算图片左上角的X坐标位置
        draw_y = self.base_y-self.rh+self.current_offset+self.shake #计算Y坐标：基准位置+正弦波动位移+碰撞震动位移。
        screen.blit(self.image,(draw_x, draw_y)) #将荷叶的图像放到计算好的屏幕坐标上

#绘制彩色雨滴
class Raindrop:
    def __init__(self,start_x=None,start_y=None):
        #构造雨滴的生成函数，固定位置生成或随机生成。
        self.start_x = start_x
        self.start_y = start_y
        #确定雨滴的起始坐标，在屏幕上方和两侧随机产生
        self.reset()

    def reset(self):
        if self.start_x is not None:
            self.x = self.start_x
            self.y = self.start_y
        else:
            self.x = random.randint(-200,WIDTH+200)
            self.y = random.randint(-200,0)
         #确定雨滴的起始坐标，没有初始值时，在屏幕上方和两侧随机产生
        self.color = (random.randint(100,255), random.randint(100,255), random.randint(200, 255))
        self.speed = random.uniform(8,14)
        self.length = random.randint(12,22)
         #初始化雨滴的颜色、下落速度、和雨滴显示出来的长度
        self.state = 0 #设置初始状态的标签
        self.target_y = random.randint(int(HEIGHT*0.75),HEIGHT-20)
          #设定水面高度，作为不击中荷叶时的终点
        self.ripple_radius = 0
        self.ripple_alpha = 255
          #初始化涟漪的半径和透明度。
        self.particles = [] #用于存储击中荷叶后的溅射的水滴效果

    def update(self,wind_x,leaves,sounds):
        if self.state == 0: #在正常的下落过程中
            self.x += wind_x
            self.y += self.speed
            #水平方向坐标随风偏移，垂直方向坐标随重力下坠。
            for leaf in leaves: #遍历所有荷叶，检测荷叶是否被雨滴击中
                dx = (self.x-leaf.base_x)/leaf.rw
                dy = (self.y-(leaf.base_y+leaf.current_offset))/leaf.rh
                #计算相对于荷叶中心的水平方向X和竖直方向Y的距离。
                if dx*dx+dy*dy <= 1: #判定雨滴下落的范围是否子啊椭圆区域内：若在椭圆内，则判定为击中荷叶。
                    self.state = 1
                    self.hit_type = "leaf"
                    # 切换到“落到荷叶上”的状态，类型设为“荷叶”
                    leaf.shake = 5 #给荷叶随机一个冲击力
                    random.choice(sounds).play() #随机播放一个水滴的声音
                    for _ in range(8):
                        self.particles.append(Particle(self.x,self.y,self.color))
                        #生成8个水珠粒子，这个水珠粒子的个数可以在后面的更新进行随机化
                    return
            if self.y >= self.target_y: #若没碰荷叶但到达水面高度，切换类型为水面
                self.y = self.target_y
                self.state = 1
                self.hit_type = "water"
                #改变状态为状态1，类型为“水面”
        elif self.state == 1:
            if self.hit_type == "water":
                self.ripple_radius += 2.5 #涟漪的半径扩大，模拟水滴刚滴入水面的情景
                self.ripple_alpha -= number_setting["fade_speed"] #涟漪淡出画面
                if self.ripple_alpha <= 0: self.state = 2
                    #涟漪淡出到看不见后，当前粒子的状态为2，之后的更新要将该粒子清除
            else:
                for p in self.particles:p.update() #如果雨滴落到荷叶上，调用水滴散开的函数
                self.particles = [p for p in self.particles if p.life>0]
                if not self.particles:self.state = 2

    def draw(self, screen, wind_x):
        if self.state == 0: #状态为0：根据风向画一条倾斜的线段
            pygame.draw.line(screen,self.color,(self.x,self.y),(self.x+wind_x,self.y+self.length),2)
        elif self.state == 1: #状态为1：在水面就绘制涟漪，在荷叶上就绘制散开的水珠
            if self.hit_type == "water":
                if self.ripple_radius < number_setting["max_ripple"]:
                    s = pygame.Surface((300,300),pygame.SRCALPHA)
                    r = self.ripple_radius
                    pygame.draw.ellipse(s, (*self.color,int(max(0,self.ripple_alpha))),
                                        (150-r,150-r//2,r*2,r),1)
                    screen.blit(s,(self.x-150,self.y-150))
            else:
                for p in self.particles:p.draw(screen)

#构建水珠落到荷叶上散开的情况
class Particle:
    def __init__(self,x,y,color):
        self.x,self.y = x,y #记录粒子的当前位置
        self.vx,self.vy = random.uniform(-4,4),random.uniform(-7,-3)
        #随机产生一个左右扩散的速度，赋予一个向上（负方向）的随机初速度，模拟溅起的效果，这一步非常重要，要不无法出现溅起来的效果
        self.life = 255 #模拟消失的参数，用于调整透明度
        self.color = color #溅起来的水珠颜色与雨滴本身的颜色相同

    def update(self):
        self.x += self.vx
        self.y += self.vy
        #根据水平速度更新X位置，垂直速度更新Y位置
        self.vy += 0.3 #模拟重力对雨滴产生的效果，使其获得向上的冲力再减小转为下落
        self.life -= 15 #每一帧透明度逐渐减少，直到粒子完全消失

    def draw(self, screen):
        if self.life > 0: #只有透明度不为0，粒子还没完全消失时才执行绘制
            s = pygame.Surface((4,4),pygame.SRCALPHA)
            pygame.draw.circle(s,(*self.color,self.life),(2, 2),2)
            screen.blit(s,(self.x,self.y))

#绘制控制按键
def draw_button(screen, text, x, y, w, h, hover):
    color = (60,180,100) if hover else (40,120,60) #设定颜色
    pygame.draw.rect(screen, color, (x,y,w,h), border_radius=10)
    font = pygame.font.SysFont("SimHei",24) #设定字体
    txt = font.render(text, True, (255,255,255)) #绘制文字
    screen.blit(txt, (x+(w-txt.get_width())//2,y+(h-txt.get_height())//2))
    return pygame.Rect(x,y,w,h)

#绘制加减按键
def draw_config_row(screen, label, val, x, y):
    font = pygame.font.SysFont("SimHei", 24)
    txt = font.render(f"{label}: {val:.1f}" if isinstance(val,float) else f"{label}: {val}", True, "White")
    screen.blit(txt,(x, y))
    btn_minus = draw_button(screen,"-", x+250,y-5,40,30,False)
    btn_plus = draw_button(screen,"+",x+300,y-5,40,30,False)
    return btn_minus,btn_plus

def main():
    pygame.init()
    pygame.mixer.init(buffer=512)
    #绘制初始界面
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("池塘夜降雨")
    clock = pygame.time.Clock()
    MENU_BACKGROUND = pygame.image.load('F:/Python_programme/colourful_rains/image/start_background.png')
    POND = pygame.image.load('F:/Python_programme/colourful_rains/image/pond.png')
    POND_BACKGROUND = pygame.transform.scale(POND, (WIDTH, HEIGHT*1.2))

    sounds = [generate_water_plink(f) for f in FREQ]
    thunder_sound = pygame.mixer.Sound('F:/Python_programme/colourful_rains/audio/thunder.mp3')

    leaves = [LotusLeaf(250,550,80,40), LotusLeaf(550,620,120,60), LotusLeaf(850,580,90,45)]
    raindrops = []
    clouds = []

    state = MENU
    wind_dir = 1
    lightning_timer = 0
    lightning_stop = 0

    # 按钮变量初始化
    btn_start = btn_info = btn_return = btn_back = pygame.Rect(0,0,0,0)
    m1 = p1 = m2 = p2 = m3 = p3 = m4 = p4 = pygame.Rect(0,0,0,0)

    run = True
    while run:
        mx,my = pygame.mouse.get_pos() #获取鼠标当前坐标，用于按钮判断
        screen.fill((5,10,20))
        # 处理退出、鼠标点击、按键等所有输入事件。
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if state == MENU:
                    if btn_start.collidepoint(event.pos): state = GAME
                    if btn_info.collidepoint(event.pos): state = INFO
                    if btn_return.collidepoint(event.pos): run = False
                    if m1.collidepoint(event.pos): number_setting["density"] = max(0.1, number_setting["density"] - 0.1)
                    if p1.collidepoint(event.pos): number_setting["density"] = min(2.0, number_setting["density"] + 0.1)
                    if m2.collidepoint(event.pos): number_setting["fade_speed"] = max(2, number_setting["fade_speed"] - 1)
                    if p2.collidepoint(event.pos): number_setting["fade_speed"] = min(30, number_setting["fade_speed"] + 1)
                    if m3.collidepoint(event.pos): number_setting["max_ripple"] = max(20, number_setting["max_ripple"] - 5)
                    if p3.collidepoint(event.pos): number_setting["max_ripple"] = min(150, number_setting["max_ripple"] + 5)
                    if m4.collidepoint(event.pos): number_setting["wind_mag"] = max(0, number_setting["wind_mag"] - 1)
                    if p4.collidepoint(event.pos): number_setting["wind_mag"] = min(20, number_setting["wind_mag"] + 1)
                elif state in [INFO,GAME]:
                    if btn_back.collidepoint(event.pos): state = MENU
            #设置键盘控制的具体内容
            if event.type == pygame.KEYDOWN and state == GAME:
                if event.key == pygame.K_UP:number_setting["density"] = min(2.0, number_setting["density"] + 0.1)
                if event.key == pygame.K_DOWN:number_setting["density"] = max(0.1, number_setting["density"] - 0.1)
                if event.key == pygame.K_RIGHT:wind_dir = 1
                if event.key == pygame.K_LEFT:wind_dir = -1
                if event.key in [pygame.K_EQUALS,pygame.K_PLUS]:number_setting["wind_mag"] = min(20,number_setting["wind_mag"] + 1)
                if event.key in [pygame.K_MINUS]:number_setting["wind_mag"] = max(0,number_setting["wind_mag"]-1)
        # 绘制初始菜单界面
        if state == MENU:
            if MENU_BACKGROUND: screen.blit(MENU_BACKGROUND,(0, 0))
            font_title = pygame.font.SysFont("SimHei",60)
            title = font_title.render("池塘夜降雨",True,'White')
            screen.blit(title, (WIDTH//2-title.get_width()//2, 60))
            m1,p1 = draw_config_row(screen,"雨滴密度",number_setting["density"],WIDTH//2-180,180)
            m2,p2 = draw_config_row(screen,"消失速度",number_setting["fade_speed"],WIDTH//2-180,230)
            m3,p3 = draw_config_row(screen,"最大水圈",number_setting["max_ripple"],WIDTH//2-180,280)
            m4,p4 = draw_config_row(screen,"风力强度",number_setting["wind_mag"], WIDTH//2-180,330)
            btn_start = draw_button(screen,"进入界面",WIDTH//2-100,400,200,50,btn_start.collidepoint(mx,my))
            btn_info = draw_button(screen,"操作说明",WIDTH//2-100,470,200,50,btn_info.collidepoint(mx,my))
            btn_return = draw_button(screen,"退出游戏",WIDTH//2-100,540,200,50,btn_return.collidepoint(mx,my))
        #绘制操作说明界面的具体内容
        elif state == INFO:
            font_info = pygame.font.SysFont("SimHei",24)
            lines = ["1.←/→键控制风向","2.加号+/减号-控制风力强度",
                     "3.↑/↓键调节雨滴密度","4.雨滴密度大于1.5后会有打雷特效"]
            for i,l in enumerate(lines):
                txt = font_info.render(l,True,(200,200,200))
                screen.blit(txt,(WIDTH//2-280,220+i*40))
            btn_back = draw_button(screen,"返回主页",50,50,150,50, btn_back.collidepoint(mx,my))
        #绘制游戏界面的具体内容
        elif state == GAME:
            if POND_BACKGROUND:screen.blit(POND_BACKGROUND,(0, 0))
            base_cloud_num = 8 #初始化乌云的数量，使得点进该界面的时候就有乌云
            target_cloud_count = int(number_setting["density"]*10)+base_cloud_num
            #根据雨滴密度计算需要的乌云数量
            if not clouds: #游戏开始时，将乌云初始化均匀分布在屏幕外的缓冲区到屏幕末端
                for i in range(target_cloud_count):
                    new_c = Black_Cloud(is_initial=True)
                    # 将X坐标均匀分布在缓冲区到屏幕末端
                    new_c.x = -300+i*((WIDTH+500)//target_cloud_count)
                    clouds.append(new_c)

            if lightning_stop > 0: lightning_stop -= 1
            if number_setting["density"] >= 1.5: #雨滴密度大于1.5的时候，触发雷电效果
                if lightning_stop <= 0 and random.random() < 0.005: #随机触发雷电，设置闪烁计时器并播放雷声
                    lightning_timer = 10
                    if thunder_sound:thunder_sound.play()
                    lightning_stop = 540

            if lightning_timer > 0:
                lightning_surf = pygame.Surface((WIDTH,HEIGHT))
                lightning_surf.fill((200,200,255))
                lightning_surf.set_alpha(150) #创建覆盖全屏的半透明蓝色层，模拟闪电照亮天空的效果
                screen.blit(lightning_surf,(0,0))
                lightning_timer -= 1

            #设置当前的风力，明确方向以及风力大小
            current_wind = wind_dir*number_setting["wind_mag"]

            #绘制荷叶
            for leaf in leaves:
                leaf.update(number_setting["wind_mag"])
                leaf.draw(screen)

            #绘制乌云以及让雨从乌云下端落下来
            if random.random() < number_setting["density"]:
                if clouds:
                    target_cloud = random.choice(clouds)
                    c_w = target_cloud.image.get_width()
                    spawn_x = random.randint(int(target_cloud.x),int(target_cloud.x+c_w))
                    spawn_y = target_cloud.y+target_cloud.image.get_height()-10
                    raindrops.append(Raindrop(spawn_x,spawn_y))
                else:
                    raindrops.append(Raindrop())

            #绘制不同帧率下变化的雨滴
            for drop in raindrops[:]:
                drop.update(current_wind,leaves,sounds)
                drop.draw(screen,current_wind)
                if drop.state == 2: raindrops.remove(drop)

            #绘制不同帧率下变化的乌云
            for cloud in clouds:
                cloud.update(current_wind)
                cloud.draw(screen)

            #返回按钮，以及右上角内容的显示
            font_hud = pygame.font.SysFont("SimHei",20)
            hud_txt = font_hud.render(f"雨滴密度:{number_setting['density']:.1f} | 风力:{number_setting['wind_mag']}",True,"White")
            screen.blit(hud_txt, (WIDTH-250,20))
            btn_back = draw_button(screen,"返回",20,20,80,40,btn_back.collidepoint(mx,my))

        pygame.display.flip()
        clock.tick(FPS) #控制帧率
    pygame.quit()

if __name__ == "__main__":
    main()