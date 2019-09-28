import win32com.client 
import sys 
import time
import random
import threading

col_button_yellow = 'f3b25e'
col_fighter_start_battle_blank = 'd33923'
col_button_start_battle = '302318'
pos_button_start_battle = (1072, 577)
pos_button_start_battle_area = (1062, 1102, 553, 592)
col_zidong = 'f7f2df'
pos_zidong = (71, 577)
pos_button_continue_invite = (724, 396)
col_fighter_auto_accept = 'edc791'
pos_jiesuan = (189, 333, 23, 76)
col_normal_accept = '54b05f'
pos_middle_monster = (509, 579, 153, 181)
pos_right_monster = (773, 856, 159, 190)

battle_failed_status = 0 

### 在这里修改是否要点怪！ ### 
# 0: 不点怪
# 1: 点中间怪
# 2: 点右边怪
emyc = 2

def mysleep(slpa, slpb = 0): 
    '''
    randomly sleep for a short time between `slpa` and `slpa + slpb` \n
    because of the legacy reason, slpa and slpb are in millisecond
    '''
    slp = random.randint(slpa, slpa+slpb) 
    time.sleep(slp/1000)

def crnd(ts, x1, x2, y1, y2): 
    '''
    randomly click a point in a rectangle region (x1, y1), (x2, y2)
    '''
    xr = random.randint(x1, x2)
    yr = random.randint(y1, y2)
    ts.MoveTo(xr, yr)
    mysleep(10, 10)
    ts.LeftClick() 
    mysleep(10, 10)

def rejxs(ts): 
    colxs = ts.GetColor(750, 458)
    #print(colxs)
    if colxs == "df715e":
        crnd(ts, 750-5, 750+5, 458-5, 458+5)
        print("successfully rejected XUAN-SHANG")
        mysleep(1000)
    mysleep(50)

def wtfc1(ts, colx, coly, coll, x1, x2, y1, y2, zzz, adv):
  '''
  Usage: 
  等待并且持续判断点 (colx, coly) 的颜色，直到该点颜色
  等于 coll (if zzz == 0) 或者 不等于 coll (if zzz == 1) 
  然后开始随机点击范围 (x1, x2) (y1, y2) 内的点，直到点 (colx, coly) 的颜色
    if adv == 1: 
     不等于 coll (if zzz == 0) 或者 等于 coll (if zzz == 1)  
    if adv == 0: 
     不判断，点击一次后退出循环
  Example: 
  在准备界面时，通过判断鼓锤上某点的颜色（因为UI不会随着游戏人物摆动），来持续点击鼓面，
  直到鼓锤上该点的颜色改变，说明进入了战斗
  '''
  j = 0
  flgj =0
  while j == 0:
    rejxs(ts)
    coltest = ts.GetColor(colx, coly)
    #print(colx, coly, coltest)
    if (coltest == coll and zzz == 0) or (coltest != coll and zzz == 1):
        flgj = 1
    if flgj == 1:
        rejxs(ts)
        crnd(ts, x1, x2, y1, y2)
        mysleep(1000, 333)
        if adv == 0:
            j = 1
        rejxs(ts)
        coltest2 = ts.GetColor(colx, coly)
        if (coltest2 == coll and zzz == 1) or (coltest2 != coll and zzz == 0):
            j = 1

def bind_two_windows(ts_d, ts_f): 
    hwnd_raw = ts_d.EnumWindowByProcess("onmyoji.exe", "", "", 16)
    hwnd = hwnd_raw.split(',')
    print('windows handle:', hwnd)

    if len(hwnd)!=2: 
        print('Need 2 windows!')
        return 10 

    # 绑定窗口
    ts_ret = ts_d.BindWindow(hwnd[0], 'dx2', 'windows', 'windows', 0) 
    if(ts_ret != 1): 
        print('first window binding failed')
        return 1
    ts_ret = ts_f.BindWindow(hwnd[1], 'dx2', 'windows', 'windows', 0) 
    if(ts_ret != 1): 
        print('second window binding failed')
        return 2
    mysleep(500)

    if ts_f.GetColor(*pos_button_start_battle) == col_button_start_battle: 
        #ts_d, ts_f = ts_f, ts_d
        print("handle swapped, don't worry")
        ts_ret = ts_d.BindWindow(hwnd[1], 'dx2', 'windows', 'windows', 0) 
        ts_ret = ts_f.BindWindow(hwnd[0], 'dx2', 'windows', 'windows', 0) 
    elif ts_d.GetColor(*pos_button_start_battle) == col_button_start_battle: 
        pass 
    else: 
        print("didn't find KAI-SHI-ZHAN-DOU, can't distinguish which one is driver ")
        return 20

    print('binding successful')
    return 0

def unbind_two_windows(ts_d, ts_f): 
    return (
        ts_d.UnBindWindow(), 
        ts_f.UnBindWindow() 
    )

def fighter_jiesuan(ts): 
    global battle_failed_status
    stats = 0 
    while stats == 0: 
        rejxs(ts)
        crnd(ts, *pos_jiesuan)

        mysleep(500, 500)

        #print('battle_failed_status =', battle_failed_status)
        if battle_failed_status == 0: 
            col_to_be_found = col_fighter_auto_accept
        else: 
            col_to_be_found = col_normal_accept

        # 找色，打手的自动接受齿轮 或 普通接受对勾
        intx, inty = None, None
        ffc_ret = ts.FindColor(16, 122, 366, 465, col_to_be_found, 1.0, 0, intx, inty)
        #print(type(ffc_ret), ffc_ret)

        if ffc_ret[0] == 0: 
            print('fighter (auto) accept found at', ffc_ret)
            wtfc1(ts, ffc_ret[1], ffc_ret[2], col_to_be_found, 
                ffc_ret[1]-5, ffc_ret[1]+5, ffc_ret[2]-5, ffc_ret[2]+5, 
                0, 1)
            print('fighter clicked (auto) accept')

        coljs = ts.GetColor(*pos_button_start_battle)
        if coljs == col_fighter_start_battle_blank: 
            print('fighter in XIE ZHAN DUI WU!')
            battle_failed_status = 0 
            stats = 1 
            break 
    print('fighter stats =', stats)

def driver_jiesuan(ts): 
    stats = 0
    while stats == 0: 
        rejxs(ts)
        crnd(ts, *pos_jiesuan)

        coljs = ts.GetColor(*pos_button_continue_invite)
        if coljs == col_button_yellow:
            if ts.GetColor(499, 321) == '725f4d': 
                # 这里意味着 勾选 继续邀请队友
                wtfc1(ts, 499, 321, '725f4d', 499-5, 499+5, 321-5, 321+5, 0, 1)
                print('ticked MO REN YAO QING DUI YOU')
            else: 
                # 如果没有这个选项，说明战斗失败，这里不需要打勾
                print('failed')
                global battle_failed_status 
                battle_failed_status = 1 
            wtfc1(ts, *pos_button_continue_invite, col_button_yellow, 
                pos_button_continue_invite[0]-5, pos_button_continue_invite[0]+5, 
                pos_button_continue_invite[1]-5, pos_button_continue_invite[1]+5, 
                0, 1)
            print('clidked QUE REN, JI XU YAO QING DUI YOU')
            #stats = 1
            #break 
        
        coljs = ts.GetColor(*pos_button_start_battle)
        if coljs == col_button_start_battle: 
            print('driver is in XIE ZHAN DUI WU')
            stats = 2 
            break 
        mysleep(500, 500)
    print('driver stats =', stats)

def dual_yuhun(ts_d, ts_f): 
    global emyc

    # 御魂战斗主循环
    while True: 
        # 司机点击开始战斗
        # 需要锁定阵容！
        wtfc1(ts_d, *pos_button_start_battle, col_button_start_battle, 
            *pos_button_start_battle_area, 0, 1)
        print('clicked KAI-SHI-ZHAN-DOU!')

        #判断是否已经进入战斗 
        while True: 
            col_d = ts_d.GetColor(pos_zidong[0], pos_zidong[1])
            col_f = ts_f.GetColor(pos_zidong[0], pos_zidong[1])
            if col_d == col_zidong or col_f == col_zidong: 
                break
            mysleep(50)
        print('in the battle!')

        # 已经进入战斗，司机自动点怪
        while True:
            rejxs(ts_d)
            rejxs(ts_f)

            # 点击中间怪物
            if emyc == 1:
                crnd(ts_d, *pos_middle_monster)

            # 点击右边怪物
            elif emyc == 2:
                crnd(ts_d, *pos_right_monster)

            mysleep(500, 500)

            rejxs(ts_d)
            rejxs(ts_f)
            col_d = ts_d.GetColor(pos_zidong[0], pos_zidong[1])
            col_f = ts_f.GetColor(pos_zidong[0], pos_zidong[1])
            if col_d != col_zidong and col_f != col_zidong: 
                break
        print('battle finished!')

        thr_f_j = threading.Thread(target=fighter_jiesuan, args=(ts_f,))
        thr_d_j = threading.Thread(target=driver_jiesuan, args=(ts_d,))

        thr_f_j.start() 
        thr_d_j.start() 

        thr_f_j.join()
        thr_d_j.join()

        print('joined, new cycle!')


def main():
    print('python version:', sys.version)

    # 需要提前在 windows 中注册 TSPlug.dll
    # 方法: regsvr32.exe TSPlug.dll

    # Reference: http://timgolden.me.uk/pywin32-docs/html/com/win32com/HTML/QuickStartClientCom.html
    # 建立 COM Object
    ts_d = win32com.client.Dispatch("ts.tssoft") 
    ts_f = win32com.client.Dispatch("ts.tssoft") 

    # 检测 COM Object 是否建立成功
    need_ver = '4.019'
    if ts_d.ver() != need_ver or ts_f.ver() != need_ver: 
        print('register failed')
        return 
    print('register successful')

    # 绑定两个游戏窗口, ts_d = driver = 司机, ts_f = fighter = 打手
    btw_ret = bind_two_windows(ts_d, ts_f)
    if btw_ret != 0: 
        return 

    try: 
        dual_yuhun(ts_d, ts_f)
    except: 
        # terminated (e.g. Ctrl + C)
        print('terminated')

        # 解绑两个窗口
        print("unbind results:", 
            unbind_two_windows(ts_d, ts_f)
        )

if __name__ == "__main__":
    main() 