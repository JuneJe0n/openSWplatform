from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from database import DBhandler
import hashlib
import os
import json
import math

application = Flask(__name__)
application.config["SECRET_KEY"] = "helloosp"

DB = DBhandler()

# Initialize an empty list to store item data
items = []

@application.route("/")
def Hello():
    return render_template("index.html")

@application.route("/mypage")
def mypage():
    return render_template("mypage.html")

@application.route("/login")
def login():
    return render_template("login.html")

@application.route("/logout")
def logout_user():
    session.clear()
    return redirect(url_for('Hello'))

@application.route("/login_confirm", methods=['POST'])
def login_user():
    id_ = request.form['id']
    pw = request.form['pw']

    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    if DB.find_user(id_, pw_hash):
        session['id'] = id_
        flash("Welcome, " + id_ + "!")
        return redirect(url_for('view_list'))  # 로그인 후 리스트 페이지로 이동
    else:
        flash("Wrong ID or Password!")
        return redirect(url_for('login'))  # 로그인 실패 시 다시 로그인 페이지로 이동


@application.route("/signup")
def signup():
    return render_template("signup.html")

@application.route("/signup_post", methods=['POST'])
def register_user():
    data=request.form
    pw=request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    if DB.insert_user(data,pw_hash):
        flash("Registration successful! Please log in.")
        return render_template("login.html")
    else:
        flash("user id already exist!")
        return render_template("signup.html")

@application.route("/check_id")
def check_id():
    id_to_check = request.args.get("id")
    if DB.user_duplicate_check(id_to_check):
        return jsonify({"available": True})
    else:
        return jsonify({"available": False})

@application.route("/list")
def view_list():
    page = request.args.get("page", 0, type=int)
    category = request.args.get("category", "all")
    per_page = 8  # item count to display per page
    per_row = 4  # item count to display per row
    row_count = int(per_page / per_row)
    start_idx = per_page * page
    end_idx = per_page * (page + 1)

    if category == "all":
        data = DB.get_items() #read the table
    else:
        data = DB.get_items_bycategory(category)

    data = dict(sorted(data.items(), key=lambda x: x[0], reverse=False)) #key는 상품명, 상품명을 사용해서 정렬
    item_counts = len(data)

    if item_counts<=per_page:
        data = dict(list(data.items())[:item_counts])
    else:
        data =dict(list(data.items())[start_idx:end_idx])

    tot_count = len(data)

    for i in range(row_count):  # last row
        if (i == row_count - 1) and (tot_count % per_row != 0):
            locals()['data_{}'.format(i)] = dict(list(data.items())[i * per_row:])
        else:
            locals()['data_{}'.format(i)] = dict(list(data.items())[i * per_row:(i + 1) * per_row])

    finalprices = {}
    if data:
        for key, item in data.items():
            price = float(item.get('price', 0))
            discount = float(item.get('discount', 0))
            finalprice = int(price * (100 - discount) * 0.01)
            finalprices[key] = finalprice


    # 이후 finalprices를 템플릿에 넘길 수 있음.
    return render_template(
        "list.html",
        datas=data.items(),
        row1=locals()['data_0'].items(),
        row2=locals()['data_1'].items(),
        limit=per_page,
        page=page,
        page_count=int(math.ceil(item_counts/per_page)),
        total=item_counts,
        finalprices=finalprices, # 템플릿으로 finalprices 전달
        category=category
    )



@application.route('/dynamicrul/<varible_name>/')
def DynamicUrl(varible_name):
    return str(varible_name)

@application.route("/detail")
def view_itemdetail():
    return render_template("detail.html")

@application.route("/view_detail/<name>/")
def view_item_detail(name):
    print("###name:",name)
    data = DB.get_item_byname(str(name))
    print("####data:",data)

    price = float(data['price'] or 0)
    discount = float(data['discount'] or 0)

    finalprice = int(price * (100 - discount) * 0.01)

    return render_template("detail.html", name=name, data=data, finalprice=finalprice)



@application.route("/review_page")
def view_review_page():
    return render_template("review_page.html")

@application.route("/reg_items")
def reg_items():
    return render_template("reg_items.html")

@application.route("/reg_review_init/<name>/")
def reg_review_init(name):
    data = DB.get_item_byname(str(name))
    return render_template("reg_reviews.html", name=name, data=data)

@application.route("/reg_reviews")
def reg_reviews():
    data = request.form
    img_list = []

    for i in range(1, 3):
        image_file = request.files.get(f'file{i}')
        if image_file:
            image_path = f"static/images/{image_file.filename}"
            image_file.save(image_path)
            img_list.append(image_path)
    
    DB.insert_review(data, img_list)
    return render_template("review_page.html")

@application.route("/submit_item_post", methods=['POST'])
def submit_item_post():
    data = request.form
    img_list = []
    opt_list = [opt for opt in request.form.getlist('option[]') if opt.strip()]
    info = request.form.get('info')

    # 이미지 파일 저장 및 경로 리스트에 추가
    for i in range(1, 10):  # 최대 9개의 이미지를 처리
        image_file = request.files.get(f'file{i}')
        if image_file:
            image_path = f"static/images/{image_file.filename}"
            image_file.save(image_path)
            img_list.append(image_path)
    
    DB.insert_item(data['name'], data, img_list, opt_list)


    page = request.args.get("page", 0, type=int)
    per_page=8 # item count to display per page
    per_row=4 # item count to display per row
    row_count=int(per_page/per_row)
    start_idx=per_page*page
    end_idx=per_page*(page+1)
    data = DB.get_items() #read the table
    item_counts=len(data)
    data=dict(list(data.items())[start_idx:end_idx])
    tot_count = len(data)
    for i in range(row_count):#last row
        if (i == row_count-1) and (tot_count%per_row != 0):
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:])
        else: 
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:(i+1)*per_row])

    finalprices = {}
    if data:
        for key, item in data.items():
            price = float(item.get('price', 0))
            discount = float(item.get('discount', 0))
            finalprice = int(price * (100 - discount) * 0.01)
            finalprices[key] = finalprice

    return render_template( 
        "list.html",
        datas=data.items(), 
        row1=locals()['data_0'].items(), 
        row2=locals()['data_1'].items(), 
        limit=per_page,
        page=page, page_count=int((item_counts/per_page)+1),
        total=item_counts,
        finalprices=finalprices,
        info=info)

@application.route("/submit_review_post", methods=['POST'])
def submit_review_post():
    data = request.form
    img_list = []

    for i in range(1, 3):
        image_file = request.files.get(f'file{i}')
        if image_file:
            image_path = f"static/images/{image_file.filename}"
            image_file.save(image_path)
            img_list.append(image_path)
    
    DB.insert_review(data, img_list)
    
    return render_template("list.html", items=items)

# 장바구니에 항목 추가
@application.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    return render_template('shoppingcart.html')


# 장바구니 페이지
@application.route('/shoppingcart')
def view_cart():
    return render_template('shoppingcart.html')

#커스터마이징 요청서
@application.route('/customizing')
def customazing():
    name = request.args.get('name')
    image = request.args.get('image')
    price = request.args.get('price')
    
    return render_template('customizing.html', name=name, image=image, price=price)

@application.route('/buying')
def buying():
    name = request.args.get('name')
    image = request.args.get('image')
    total_price = request.args.get('totalPrice')
    discount = request.args.get('discount')

    options_json = request.args.get('selectedOption')  # JSON 형식으로 전달받음
    options = json.loads(options_json)

    return render_template('buying.html', name=name, image=image, total_price=total_price, options=options, discount=discount)


#찜 기능
@application.route('/show_heart/<name>/', methods=['GET'])
def show_heart(name):
    print("###show_heart#####",session['id'],name)
    my_heart = DB.get_heart_byname(session['id'],name)
    print("####show_heart####",my_heart)
    return jsonify({'my_heart': my_heart})

@application.route('/like/<name>/', methods=['POST'])
def like(name):
    image = request.form.get('image')
    my_heart = DB.update_heart(session['id'],'Y',name, image)
    return jsonify({'msg': '좋아요 완료!'})

@application.route('/unlike/<name>/', methods=['POST'])
def unlike(name):
    image = request.form.get('image')
    my_heart = DB.update_heart(session['id'],'N',name, image)
    return jsonify({'msg': '안좋아요 완료!'})


@application.route('/likelist')
def likelist():
    user_id = session.get('id')
    like_items = []

    if user_id:
        hearts = DB.db.child("heart").child(user_id).get()

        if hearts.val():
            for heart in hearts.each():
                item_name = heart.key()  # 아이템 이름
                item_data = heart.val()  # 찜 데이터
                
                # 관심 데이터만 추가
                if item_data.get('interested') == 'Y':
                    like_items.append({
                        "name": item_name,
                        "image": item_data.get("image"),  # 이미지 추가
                        "data": item_data
                    })
    
    return render_template('likelist.html', like_items=like_items)



if __name__ == "__main__":
    application.run(host='0.0.0.0', debug=True)
