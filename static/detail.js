{% extends "index.html" %}

{% block extra_css %}
<link rel="stylesheet" href="/static/detail.css">
{% endblock %}

{% block content %}
<input type="hidden" name="seller" id="seller" value="{{session['nickname']}}">
<div class="detail">
    <div class="detail-image">
        <img id="center_img" src="/{{data.images[0]}}" alt="center_img" width="550px" height="450px">
        <div style="margin-top: 15px; display: flex; justify-content: center;">
            {% for i in range(0, 9) %}
                {% if data.images[i] %}
                    <img class="thumbnail" src="/{{data.images[i]}}" alt="other_img" width="55px" height="45px" onclick="changeCenterImage(this)">
                {% endif %}
            {% endfor %}
        </div>
    </div>    



        <label class="detail-info">
            <p style="color:gray;"><img src="/static/images/user_icon.png" alt="user_icon" width="30" height="30">
                {{data.seller}}</p>
            <p style="font-size:30px; margin: 20px 0;"><b>{{name}}</b></p>
            <p style="color:gray; display: flex; justify-content: flex-end; margin: 0;"><del id="price">{{data.price}}원</del></p>
                <p style="font-size: 30px; display: flex; justify-content: flex-end; margin: 10px 0;"><b>
                <span style="color:red; font-size: 40px; margin-right: 10px;">{{data.discount}}%</span>
                <span id="finalPrice">{{ finalprice }}</span>
            </b></p>

            <select id="option" style="width: 100%; height: 10%; margin: 10px 0;">
                <option value="" disabled selected>옵션 선택</option>
                {% for i in range(0, data.options | length) %}
                    {% if data.options[i] %}
                        <option value="{{data.options[i]}}" style="margin: 0">{{ data.options[i] }}</option>
                    {% endif %}
                {% endfor %}
            </select>
            <div id="selectedOptions"></div>
            <template id="optionTemplate">
                <div class="newoptionDiv">
                    <span class="optionText"></span>
                    <input type="number" class="quantity-input" min="1" max="100" value="1">
                </div>
            </template>

            <hr>
            <p style="display: flex; justify-content: flex-end; align-items: flex-end; margin: 20px 0;">총 금액
            <span id="totalPrice" style="font-size:30px;  margin-left: 10px;"><b>0원</b></span></p>

            <form action="/add_to_cart" method="POST" onsubmit="return false;">
                <input type="hidden" name="name" value="{{ name }}">
                <input type="hidden" name="image" value="{{ data.images[0] }}">
                <input type="hidden" name="discount" value="{{ data.discount }}">
                <input type="hidden" name="price" value="{{ finalprice }}">
                <input type="hidden" name="totalPrice" id="totalPrice">
                <input type="hidden" name="selectedOption" id="selectedOptionInput">
                
                <div style="float: right; margin: 20px 0;">
                    <div style="margin-bottom: 10px;">
                        <button onclick="addToCart('{{ name }}', '{{ data.images[0] }}', '{{ data.price }}', '{{ data.discount }}', '{{ finalprice }}')"
                            style="border: none; border-radius: 4px; width: 100px; height: 30px; font-size: 15px; margin-right: 10px;">
                            장바구니
                        </button>
                        <input type="button" value="구매하기" 
                            style="background-color:#006400; color: white; border: none; border-radius: 4px; width: 100px; height: 30px; font-size: 15px;"
                            onclick="buyingItem()">
                    </div>
                    {% if data.custom == "1" %}
                        <input type="button" value="커스터마이징 요청하기" 
                            style="margin-left:10px; background-color:aliceblue; border: none; border-radius: 4px; width: 200px; height: 30px; font-size: 15px;"
                            onclick="location.href='/apply_custom_init/{{name}}/';">
                    {% endif %}
                </div>
            </form>
            
            {% if name %}
                <button onclick="location.href='/reg_review_init/{{name}}/';">리뷰 등록</button>
                <i class="fa fa-heart" id="heart" ></i>
            {% endif %}
        </label>
    </div>

    <div id="cartModal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 1000; justify-content: center; align-items: center;">
        <div style="background: white; padding: 20px; border-radius: 5px; width: 50%; max-width: 400px; text-align: center;">
            <h2>장바구니</h2>
            <p>상품이 장바구니에 추가되었습니다.</p>
            <button onclick="closeCartModal()" style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer;">확인</button>
        </div>
    </div>

    <footer>
        <div class="footer_nav">
            <ul>
                <li><a onclick="loadIframe('/detail_info', this)" class="active">상품 설명</a></li>
                <li><a onclick="loadIframe('/review_page/{{name}}/', this)">리뷰</a></li>
                <li><a onclick="loadIframe('/seller_email', this)">판매자 메일</a></li>
            </ul>
        </div>
    
        <div id="iframe_container" style="margin-top: 20px;">
            <iframe id="footer_iframe" src="" style="width: 100%; border: none;" hidden></iframe>
        </div>
    </footer>
    

    {% endblock %}
    {% block extra_js %}
    <script src="/static/detail.js"></script>
    
    {% endblock %}
