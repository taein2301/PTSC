/*
 * ============================================================================
 * LoadRunner C 스크립트
 * ============================================================================
 *
 * 변환 정보:
 *   - 원본: JMeter Test Plan (Complex E-commerce Scenario)
 *   - 변환 도구: Performance Test Script Converter (PTSC)
 *   - 생성일: 자동 변환
 *
 * 주의사항:
 *   이 스크립트는 자동으로 변환되었습니다.
 *   프로덕션 환경에서 사용하기 전에 반드시 검토 및 테스트를 수행하세요.
 *
 * ============================================================================
 */

#include "web_api.h"
#include "lrun.h"
#include "web_custom_body.h"

/*
 * ============================================================================
 * Runtime Settings 설정 가이드
 * ============================================================================
 *
 * 가상 사용자(Vuser) 설정:
 *   - Run Logic > Vuser: 동시 실행할 가상 사용자 수 설정
 *   - Run Logic > Start: 가상 사용자 시작 방식 (동시/순차)
 *   - Run Logic > Run: 반복 횟수 또는 실행 시간 설정
 *
 * Think Time 설정:
 *   - Think Time > Think time: lr_think_time() 함수 처리 방식
 *   - Think Time > Random: Think time에 무작위성 추가
 *
 * 파라미터(Parameter) 설정:
 *   - Parameters > Parameter List: 새 파라미터 추가 및 관리
 *   - 파라미터 타입:
 *     • File: 파일에서 데이터 읽기 (CSV, DAT 등)
 *     • Table: 테이블 형태로 데이터 입력
 *     • User Defined Function: 사용자 정의 함수로 생성
 *   - Select Next Row: 다음 값 선택 방식
 *     • Sequential: 순차적 선택
 *     • Random: 무작위 선택
 *     • Unique: 중복 없이 선택
 *   - Update Value On: 값 갱신 시점
 *     • Each iteration: 매 반복마다
 *     • Each occurrence: 매번 사용할 때마다
 *     • Once: 한 번만
 *   - When Out of Values: 값이 부족할 때 처리
 *     • Abort Vuser: Vuser 중단
 *     • Continue in a cyclic manner: 처음부터 다시 반복
 *     • Continue with last value: 마지막 값 계속 사용
 *
 * 로그 설정:
 *   - Log > Enable logging: 로그 활성화
 *   - Log > Extended log: 상세 로그 레벨 설정
 *   - Log > Always send messages: 모든 메시지 전송
 *   - Log > Log on error: 에러 발생 시에만 로그
 *
 * ============================================================================
 */



/*
 * ============================================================================
 * vuser_init - 가상 사용자 초기화
 * ============================================================================
 * 설명:
 *   각 가상 사용자(Vuser)가 스크립트 실행을 시작하기 전에 한 번 실행됩니다.
 *   로그인 정보, 전역 변수 등을 초기화하는 용도로 사용됩니다.
 *
 * 실행 시점:
 *   - Action 함수 실행 전
 *   - 각 Vuser당 1회만 실행
 * ============================================================================
 */
vuser_init()
{
	// ========================================
	// 초기 설정
	// ========================================
	// 초기 대기 시간 (1초)
	lr_think_time(1);

	return 0;
}



/*
 * ============================================================================
 * Action - 메인 비즈니스 로직
 * ============================================================================
 * 설명:
 *   실제 부하 테스트 시나리오가 실행되는 메인 함수입니다.
 *   HTTP 요청, 트랜잭션, 검증 등 주요 비즈니스 로직이 포함됩니다.
 *
 * 실행 시점:
 *   - vuser_init 실행 후
 *   - Runtime Settings에 설정된 횟수만큼 반복 실행
 *   - vuser_end 실행 전
 * ============================================================================
 */
Action()
{
	// Add headers
	web_add_header("User-Agent", "LoadRunner-Test");
	web_add_header("Accept", "application/json");

	// ======================================== 트랜잭션 시작: Browse Products ========================================
	lr_start_transaction("Browse Products");

    // ----------------------------------------
    // 상관관계(Correlation): sessionId
    // 좌측 경계(LB): sessionId=
    // 우측 경계(RB): 
    // 추출 순서: 1번째 값
    // 주의: 이 함수는 HTTP 요청 전에 위치해야 합니다
    // ----------------------------------------
    web_reg_save_param("sessionId", 
        "LB=sessionId=", 
        "RB=", 
        "Ord=1", 
        "Search=Body", 
        "RelFrameID=All", 
        LAST );
	// ----------------------------------------
	// HTTP 요청: Homepage
	// 메서드: GET
	// URL: http://{BASE_URL}/
	// ----------------------------------------
    web_url("Homepage", 
        "URL=http://{BASE_URL}/", 
        "Resource=0", 
        "RecContentType=text/html", 
        "Referer=", 
        "Snapshot=t1.inf", 
        "Mode=HTML", 
        LAST );

	// Think Time: 1500ms = 1.5초 대기
	lr_think_time(1.5);

    // ----------------------------------------
    // 상관관계(Correlation): productId
    // 좌측 경계(LB): 
    // 우측 경계(RB): 
    // 추출 순서: 1번째 값
    // 주의: 이 함수는 HTTP 요청 전에 위치해야 합니다
    // ----------------------------------------
    web_reg_save_param("productId", 
        "LB=", 
        "RB=", 
        "Ord=1", 
        "Search=Body", 
        "RelFrameID=All", 
        LAST );
	// ----------------------------------------
	// HTTP 요청: Product List
	// 메서드: GET
	// URL: http://{BASE_URL}/api/products?session={sessionId}
	// ----------------------------------------
    web_url("Product List", 
        "URL=http://{BASE_URL}/api/products?session={sessionId}", 
        "Resource=0", 
        "RecContentType=text/html", 
        "Referer=", 
        "Snapshot=t2.inf", 
        "Mode=HTML", 
        LAST );

	// ======================================== 트랜잭션 종료: Browse Products ========================================
	lr_end_transaction("Browse Products", LR_AUTO);

	// ======================================== 트랜잭션 시작: Add to Cart ========================================
	lr_start_transaction("Add to Cart");

	// ----------------------------------------
	// HTTP 요청: Add Product to Cart
	// 메서드: POST
	// URL: http://{BASE_URL}/api/cart/add
	// ----------------------------------------
    web_submit_data("Add Product to Cart", 
        "Action=http://{BASE_URL}/api/cart/add", 
        "Method=POST", 
        "RecContentType=text/html", 
        "Referer=", 
        "Snapshot=t3.inf", 
        "Mode=HTML", 
        LAST );

	// ======================================== 트랜잭션 종료: Add to Cart ========================================
	lr_end_transaction("Add to Cart", LR_AUTO);

	// ======================================== 루프 시작: View Multiple Products (반복 3회) ========================================
    for (int loop_i = 0; loop_i < 3; loop_i++)
    {

			// ----------------------------------------
			// HTTP 요청: View Product Details
			// 메서드: GET
			// URL: http://{BASE_URL}/product/{productId}
			// ----------------------------------------
		    web_url("View Product Details", 
		        "URL=http://{BASE_URL}/product/{productId}", 
		        "Resource=0", 
		        "RecContentType=text/html", 
		        "Referer=", 
		        "Snapshot=t4.inf", 
		        "Mode=HTML", 
		        LAST );

    }
	// ======================================== 루프 종료: View Multiple Products ========================================

	// ======================================== 트랜잭션 시작: Checkout ========================================
	lr_start_transaction("Checkout");

	// ----------------------------------------
	// HTTP 요청: Checkout API
	// 메서드: POST
	// URL: http://{BASE_URL}/api/checkout
	// ----------------------------------------
    web_submit_data("Checkout API", 
        "Action=http://{BASE_URL}/api/checkout", 
        "Method=POST", 
        "RecContentType=text/html", 
        "Referer=", 
        "Snapshot=t5.inf", 
        "Mode=HTML", 
        ITEMDATA, 
        "Name=session", "Value={sessionId}", ENDITEM, 
        "Name=payment", "Value=credit_card", ENDITEM, 
        LAST );

	// ======================================== 트랜잭션 종료: Checkout ========================================
	lr_end_transaction("Checkout", LR_AUTO);

	return 0;
}



/*
 * ============================================================================
 * vuser_end - 가상 사용자 종료
 * ============================================================================
 * 설명:
 *   각 가상 사용자(Vuser)가 스크립트 실행을 종료한 후 한 번 실행됩니다.
 *   연결 해제, 리소스 정리 등을 수행하는 용도로 사용됩니다.
 *
 * 실행 시점:
 *   - Action 함수 실행 후
 *   - 각 Vuser당 1회만 실행
 * ============================================================================
 */
vuser_end()
{
	// ========================================
	// 종료 처리
	// ========================================
	// 필요시 로그아웃, 연결 해제 등의 정리 작업을 수행합니다

	return 0;
}