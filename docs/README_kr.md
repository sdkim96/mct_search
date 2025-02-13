### 🎯 MCT Search (몬테카를로 트리 탐색)

이 저장소는 OpenAI Chat Completion을 활용하여 주어진 질의에 대한 **해답(Solution)** 을 생성하고, 이를 **Pydantic** 모델을 사용해 반영(Reflection)한 후, **몬테카를로 트리(MCT, Monte Carlo Tree)** 방식으로 탐색하는 예제를 제공합니다.

---

## 🦜 빠른 시작 (QuickStart)

이 코드를 실행하려면 `poetry` 의존성이 필요합니다.  
Poetry 사용법은 [공식 문서](https://python-poetry.org/docs/)를 참고하세요.

```sh
poetry install
poetry shell
python -m app.main "who is the best person in the world?"
```
그럼 최종 결과가 JSON 파일로 저장됩니다!

## 👀 개요 (Overview)

### 주요 파일 설명

- **`models.py`**:  
  **Pydantic**을 사용하여 데이터 모델을 정의합니다.
  - **Answer**: 주요 응답과 설명을 포함하는 모델
  - **Solution**: 질의(`query`)와 이에 대한 해답(`Answer`)을 포함하는 모델
  - **Reflection**: 반영(Reflection) 텍스트, 점수, 유효한 해답인지 여부를 포함하는 모델
  - **NodeSnapshot**, **EdgeSnapshot**, **TreeSnapshot**: 트리 구조(노드, 엣지, 솔루션, 반영 결과 등)를 저장하는 스냅샷 모델

- **`chat.py`**:  
  OpenAI Chat Completion API를 호출하여 Pydantic 모델로 변환하는 `invoke` 함수를 포함합니다.
  - **`solve(query, context) -> Solution`**: 질의와 컨텍스트를 받아 해답을 생성하는 함수
  - **`reflect(solution) -> Reflection`**: 해답을 평가하고 점수를 부여하는 함수

- **`tree.py`**:  
  **몬테카를로 트리(Monte Carlo Tree)** 기반으로 해답을 탐색하는 알고리즘을 구현합니다.
  - **트리 탐색 단계**:
    1. **선택(Selection)**: 가장 유망한 노드를 선택
    2. **확장(Expansion)**: 선택된 노드에서 새로운 해답 생성
    3. **반영(Reflection)**: 해답을 평가하고 점수 부여
    4. **역전파(Backpropagation)**: 평가 점수를 부모 노드로 전파

---

## 🌲 몬테카를로 트리 탐색 (MCT Algorithm)

몬테카를로 트리 탐색(MCTS)은 **선택(Selection)**, **확장(Expansion)**, **시뮬레이션(Simulation)**, **역전파(Backpropagation)** 의 네 가지 단계로 이루어집니다.

1. **선택 (Selection)**  
   - 가장 유망한 노드를 선택하여 탐색을 진행합니다.
   - `tree.py`에서는 값이 가장 높은 노드를 선택하는 간단한 방식 사용.

2. **확장 (Expansion)**  
   - 선택된 노드에서 새로운 자식 노드를 생성합니다.
   - `chat.solve(query)`를 사용해 해답을 생성하고, `chat.reflect(solution)`을 호출해 평가합니다.
   - 생성된 해답과 평가 점수를 기반으로 트리에 새로운 노드를 추가.

3. **(경량) 시뮬레이션 (Light Simulation)**  
   - 일부 MCTS에서는 무작위 시뮬레이션을 실행하여 결과를 예측하지만, 여기서는 생략됨.
   - 대신, `chat.solve` 호출 자체가 일종의 단일 단계 "시뮬레이션" 역할을 수행.

4. **역전파 (Backpropagation)**  
   - 반영된 평가 점수를 부모 노드로 전파하여 탐색 방향을 조정.
   - 이를 통해 더 나은 해답을 찾을 수 있도록 트리를 최적화.

이 과정을 여러 번 반복하여 최적의 해답을 찾습니다.

---

## ⚙️ 실행 흐름 (Execution Flow)

1. **트리 생성 및 설정**  
   `MonteCarloTree` 객체를 생성할 때 다음과 같은 설정을 지정할 수 있습니다.
   - `depth_limit`: 최대 탐색 깊이
   - `leafs_limit`: 각 단계에서 확장할 자식 노드 개수
   - `snapshot=True`로 설정하면 탐색 과정 스냅샷 저장 가능

2. **탐색 실행**  
   - `run(query, loop, pre_terminate)` 호출:
     - **선택 → 확장 → 반영 → 역전파** 단계를 반복
     - `loop` 횟수만큼 반복 실행하며, `pre_terminate=True`인 경우 유효한 해답이 발견되면 조기 종료

3. **결과 확인**  
   - 유효한 해답이 발견되면 `Solution` 객체로 반환.
   - 주어진 탐색 깊이 또는 반복 횟수 내에서 해답을 찾지 못하면 `None` 반환.

4. **(선택적) 스냅샷 저장**  
   - `snapshot=True` 설정 시, 트리 구조(노드, 엣지, 솔루션, 반영 결과 등)를 JSON 파일로 저장.

---