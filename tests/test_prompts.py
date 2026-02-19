from verdictswarm_mcp.server import portfolio_check, scoring_resource, should_i_buy


def test_should_i_buy_prompt_contains_expected_content():
    prompt = should_i_buy("TokenAddr123", chain="solana")
    assert "Token: TokenAddr123 on solana" in prompt
    assert "Overall recommendation (BUY / HOLD / AVOID)" in prompt
    assert "If this looks like a scam, say so clearly." in prompt


def test_portfolio_check_prompt_contains_expected_content():
    prompt = portfolio_check("A1,B2,C3", chain="base")
    assert "Chain: base" in prompt
    assert "Tokens (comma-separated addresses): A1,B2,C3" in prompt
    assert "Classify as KEEP / REDUCE / EXIT" in prompt


def test_scoring_resource_contains_grade_ranges():
    scoring = scoring_resource()
    assert "VerdictSwarm scoring guide (0-100):" in scoring
    assert "80-100" in scoring
    assert "0-39" in scoring
