#!/bin/bash
# Test CS Navigator with 20 complex queries
# Each query gets a fresh session to avoid context bleeding

BASE_URL="http://127.0.0.1:8000"
APP="cs_navigator_unified"
USER="test_user"
PASS=0
FAIL=0
TOTAL=0

# Function to test a query
test_query() {
    local query="$1"
    local test_num="$2"
    TOTAL=$((TOTAL + 1))

    # Create fresh session
    SESSION=$(curl -s -X POST "$BASE_URL/apps/$APP/users/$USER/sessions" \
        -H "Content-Type: application/json" \
        -d '{"state": {}}' | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

    # Send query and measure time
    START=$(python3 -c "import time; print(time.time())")

    RESPONSE=$(curl -s -X POST "$BASE_URL/run_sse" \
        -H "Content-Type: application/json" \
        --max-time 60 \
        -d "{\"app_name\": \"$APP\", \"user_id\": \"$USER\", \"session_id\": \"$SESSION\", \"new_message\": {\"role\": \"user\", \"parts\": [{\"text\": \"$query\"}]}}" 2>&1)

    END=$(python3 -c "import time; print(time.time())")
    DURATION=$(python3 -c "print(f'{$END - $START:.1f}s')")

    # Extract the final text answer (last model response with text)
    ANSWER=$(echo "$RESPONSE" | grep '"text"' | tail -1 | python3 -c "
import sys, json
for line in sys.stdin:
    line = line.strip()
    if line.startswith('data: '):
        line = line[6:]
    try:
        d = json.loads(line)
        parts = d.get('content',{}).get('parts',[])
        for p in parts:
            if 'text' in p:
                text = p['text'][:200].replace('\n',' ').strip()
                print(text)
                break
    except:
        pass
" 2>/dev/null)

    # Extract which agent was called
    AGENT=$(echo "$RESPONSE" | grep '"functionCall"' | head -1 | python3 -c "
import sys, json
for line in sys.stdin:
    line = line.strip()
    if line.startswith('data: '):
        line = line[6:]
    try:
        d = json.loads(line)
        parts = d.get('content',{}).get('parts',[])
        for p in parts:
            if 'functionCall' in p:
                print(p['functionCall']['name'])
                break
    except:
        pass
" 2>/dev/null)

    if [ -z "$ANSWER" ]; then
        ANSWER="[NO RESPONSE]"
        FAIL=$((FAIL + 1))
        STATUS="FAIL"
    else
        PASS=$((PASS + 1))
        STATUS="OK"
    fi

    echo ""
    echo "━━━ TEST $test_num [$STATUS] ($DURATION) → $AGENT ━━━"
    echo "Q: $query"
    echo "A: ${ANSWER:0:300}"
}

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   CS Navigator - 20 Query Stress Test                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# === ACADEMIC ADVISING ===
test_query "Who is the chair of the Computer Science department?" 1
test_query "What are the prerequisites for COSC 320 Analysis of Algorithms?" 2
test_query "Which professors do research in artificial intelligence and machine learning?" 3

# === COURSE RECOMMENDATIONS ===
test_query "What courses should I take if I want to specialize in cybersecurity?" 4
test_query "I am a sophomore who has completed COSC 111 and COSC 112. What should I take next?" 5
test_query "What elective courses are available for CS majors?" 6

# === CAREER GUIDANCE ===
test_query "How can I find internship opportunities in software engineering?" 7
test_query "What career resources does the CS department offer?" 8
test_query "What student organizations can help me with my CS career?" 9

# === DEGREE REQUIREMENTS ===
test_query "What are the total credit hours needed to graduate with a BS in Computer Science?" 10
test_query "What math courses are required for the CS degree?" 11
test_query "Tell me about the 4+1 Bachelor and Master program in Computer Science" 12

# === SCHEDULE BUILDING ===
test_query "Can you help me plan a schedule for my junior year in CS?" 13
test_query "Which CS courses are typically offered in the spring semester?" 14

# === FINANCIAL AID ===
test_query "What scholarships are available specifically for CS students?" 15
test_query "Are there any research assistantship opportunities in the CS department?" 16

# === GENERAL Q&A ===
test_query "Where is the Computer Science department located and what are the office hours?" 17
test_query "How do I contact the CS department for advising?" 18

# === MULTI-DOMAIN / COMPLEX ===
test_query "I want to work in AI after graduation. What courses, internships, and faculty should I connect with?" 19
test_query "I am a freshman starting CS next fall. Give me a complete roadmap including courses, organizations to join, and career prep tips." 20

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   RESULTS: $PASS passed / $FAIL failed / $TOTAL total                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
