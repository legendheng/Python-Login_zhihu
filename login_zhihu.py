import requests
import http.cookiejar as cookielib
import re
import os

session=requests.session()

#设置请求头
agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"
header={
    "Referer":"https://www.zhihu.com/",
    "User-Agent":agent
}


#获取_xsrf，作为参数用来提交
def get_xsrf():
    content=session.get("https://www.zhihu.com/#signin",headers=header).content.decode("utf-8")
    match_obj=re.search('name="_xsrf" value="(.*?)"/>',content).group(1)
    if match_obj:
        return match_obj
    else:
        print("没有获取到_xsrf")



#获取登录验证的图片，根据最下面给出的坐标参考，若需要提交多个坐标则以空格来隔开
def get_captcha():
     import time
     t=str(int(time.time()*1000))
     captcha_url="https://www.zhihu.com/captcha.gif?r={0}&type=login&lang=cn".format(t)#构造验证码网页地址
     t=session.get(captcha_url,headers=header)
     with open("captcha.jpg","wb") as f:    #写入本地
         f.write(t.content)
         f.close()
     from PIL import Image
     try:
         img=Image.open('captcha.jpg')      #写入后自动打开验证码图片并人工识别输入
         img.show()
         img.close()
     except:
         pass

     captcha=input("输入验证码：")
     final=captcha.split()              #这里用了很别扭的方法构造验证码列表，最终是[[a],[b]]这种形式，硬拼起来
     x=len(final)
     s=''
     for i in range(1,x+1):
        a=final.pop()
        if s=='':
            s=s+'['+a+']'
        else:
            s=s+',['+a+']'
     yanzhengma='{"img_size":[200,44],"input_points":['+str(s)+']}'
     return yanzhengma



#模拟知乎登陆
def zhihu_login(account,password):
    session.cookies=cookielib.LWPCookieJar(filename='cookies.txt')
    try:
        session.cookies.load(ignore_discard=True)# ignore_discard默认是false，忽略关闭浏览器丢失
    except:
        print("cookie未能加载")
    if not os.path.getsize('cookies.txt'):  #判断cookie文件是否已经有内容，第一次登录时没有
        if re.match('1\d{10}',account):
            print('手机号码登陆')
            post_url='https://www.zhihu.com/login/phone_num'
            captcha=get_captcha()
            post_data={
                "_xsrf":get_xsrf(),
                "phone_num":account,
                "password":password,
                "captcha_type":"cn",
                "captcha":captcha
            }

            session.post(post_url,data=post_data,headers=header).content.decode('utf-8')    #模拟登陆提交
            session.cookies.save()              #保存cookie值到本地
            content=session.get("https://www.zhihu.com/#signin",headers=header).content.decode("utf-8")     #获取首页内容
            print(content)
    else:
         contents=session.get("https://www.zhihu.com/#signin",headers=header).content.decode("utf-8")        #若本地的cookies.txt有保存cookie值就会直接访问
         print(contents)




# get_xsrf()    测试获取xsrf
zhihu_login("你的知乎账号","你的知乎密码")

#下面是提交验证码的坐标参数参考
#captcha:{"img_size":[200,44],"input_points":[[17.29688,24],[40.2969,25],[66.2969,24],[89.2969,24],[114.297,25],[138.297,26],[162.297,24]]}
