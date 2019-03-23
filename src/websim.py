# coding=utf-8
import json
import logging
import re
import time
import datetime

import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from hashlib import md5

import config
from string import Formatter

DELAYS_DISTRIBUTION = {
    "PRICE_VOLUME_DATA": {0,1},
    "FUNDAMENTAL_DATA": {1},
    "ANALYST_ESTIMATE_DATA": {0,1},
    "RELATIONSHIP_DATA": {0,1},
    "SENTIMENT_DATA": {0,1},
    "MODEL_DATA": {0,1},
    "US_NEWS_DATA": {0,1},
    "MODEL_RATINGS_DATA": {0,1},
    "VOLATILITY_DATA": {0,1},
    "STOCK_REPORTS_PLUS": {0,1},
    "SYSTEMATIC_RISK_METRICS": {0,1},
    "OPTIONS_ANALYTICS": {0,1},
    "STREET_EVENTS": {1},
    "ANALYST_REVISION_SCORE": {1},
    "SHORT_INTEREST_MODEL": {1},
    "EPS_ESTIMATE_MODEL": {1},
    "CREDIT_RISK_MODEL": {1},
    "PRICE_MOMENTUM_MODEL": {1},
    "INSIDER_MODEL": {1},
    "GROWTH_VALUATION_MODEL": {1},
    "SMART_RATIOS": {1},
    "SMART_HOLDINGS": {1},
    "ANALYST_REVISIONS": {1},
    "VOLATILITY_AND_RISK_FACTOR_DATA": {1},
    "EBITDA_ESTIMATE_MODEL": {1},
    "PRICE_TARGET_DATA": {1},
    "PERFORMANCE_METRICS_DATA": {1},
    "INSTITUTIONAL_OWNERSHIP_DATA": {1},
    "REVENUE_ESTIMATE_MODEL": {1}
}

OTHER_WORDS = {
    "region": {'usa', 'eur', 'asi'},
    "universe": {'usa', 'eur', 'asi'},
    "delay": {'usa', 'eur', 'asi'},
    "decay": {'usa', 'eur', 'asi'},
    "max_stock_weight": {'usa', 'eur', 'asi'},
    "neutralization": {'usa', 'eur', 'asi'},
    "lookback": {'usa', 'eur', 'asi'},
    "usa": {'usa', 'eur', 'asi'},
    "eur": {'usa', 'eur', 'asi'},
    "asi": {'usa', 'eur', 'asi'},
    "none": {'usa', 'eur', 'asi'},
    "market": {'usa', 'eur', 'asi'},
    "sector": {'usa', 'eur', 'asi'},
    "industry": {'usa', 'eur', 'asi'},
    "subindustry": {'usa', 'eur', 'asi'}
}

GROUPING_WORDS = {
    "market": {'usa', 'eur', 'asi'},
    "country": {'usa', 'eur', 'asi'},
    "exchange": {'usa', 'eur', 'asi'},
    "sector": {'usa', 'eur', 'asi'},
    "industry": {'usa', 'eur', 'asi'},
    "subindustry": {'usa', 'eur', 'asi'}
}

OPERATOR_WORDS = {
    "abs",
    "add"
    "false",
    "true",
    "divide",
    "exp",
    "floor",
    "/",
    "*",
    "-",
    "+",
    "=",
    "==",
    ">",
    "<",
    ">=",
    "<=",
    "frac",
    "inverse",
    "log",
    "log_diff",
    "max",
    "min",
    "multiply",
    "nan_mask",
    "nan_out",
    "power",
    "purify",
    "replace",
    "reverse",
    "round",
    "round0",
    "sign",
    "signed_power",
    "slog1p",
    "sqrt",
    "subtract",
    "to_nan",
    "and"
    "or",
    "equal",
    "if_else",
    "?",
    ":",
    "is_not_nan",
    "is_nan",
    "is_finite",
    "is_not_finite"
    "less",
    "greater",
    "negate"
    "arc_cos",
    "arc_sin",
    "arc_tan",
    "bucket",
    "clamp",
    "filter",
    "keep",
    "left_tail",
    "pasteurize",
    "right_tail",
    "sigmoid",
    "tail",
    "tanh",
    "trade_when",
    "normalize",
    "one_side",
    "quantile",
    "rank",
    "rank_by_side",
    "regression_neut",
    "regression_proj",
    "scale",
    "scale_down",
    "truncate",
    "vector_neut",
    "vector_proj",
    "winsorize",
    "zscore",
    "group_backfill",
    "group_count",
    "group_extra",
    "group_max",
    "group_mean",
    "group_median",
    "group_min",
    "group_neutralize",
    "group_normalize",
    "group_precentage",
    "group_rank",
    "group_scale",
    "group_stddev",
    "group_sum",
    "group_zscore",
    "days_from_last_change",
    "ts_weighted_delay",
    "hump",
    "hump_decay",
    "inst_tvr",
    "jump_decay",
    "kth_element",
    "last_diff_value",
    "ts_arg_max",
    "ts_arg_min",
    "ts_av_diff",
    "tas_co_kurtosis",
    "ts_corr",
    "ts_co_skewness",
    "ts_count_nans",
    "ts_covariance",
    "ts_decay_exp_window",
    "ts_decay_linear_window"
    "ts_decay_linear",
    "ts_delay",
    "ts_delta",
    "ts_ir",
    "ts_kurtosis",
    "ts_max",
    "ts_max_diff",
    "ts_mean",
    "ts_median",
    "ts_min",
    "ts_min_diff",
    "ts_min_max_cps",
    "ts_min_max_diff",
    "ts_moment",
    "ts_partial_corr",
    "ts_percentage",
    "ts_poly_regression",
    'ts_rank',
    "ts_returns",
    "ts_scale",
    "ts_skewness",
    "ts_stddev",
    "ts_step",
    "ts_sum",
    "ts_theilsen",
    "ts_triple_corr",
    "ts_zscore",
    "ts_regression"
    "convert",
    "instpnl"
    "||"
    "|",
    "&&",
    "!",
    "^",
    "target",
    "factor",
    "nan",
    "NaN",
    "range"
}

DATA_WORDS = {
    "PRICE_VOLUME_DATA": {
        "open": {'usa', 'eur', 'asi'},
        "close": {'usa', 'eur', 'asi'},
        "high": {'usa', 'eur', 'asi'},
        "low": {'usa', 'eur', 'asi'},
        "vwap": {'usa', 'eur', 'asi'},
        "volume": {'usa', 'eur', 'asi'},
        "returns": {'usa', 'eur', 'asi'},
        "adv20": {'usa', 'eur', 'asi'},
        "sharesout": {'usa', 'eur', 'asi'},
        "cap": {'usa', 'eur', 'asi'},
        "split": {'usa', 'eur', 'asi'},
        "dividend": {'usa', 'eur', 'asi'},
    },
    "FUNDAMENTAL_DATA": {
        "accounts_payable": {'eur', 'asi'},
        "accum_depre": {'eur', 'asi'},
        "assets": {'usa', 'eur', 'asi'},
        "assets_curr": {'usa', 'eur', 'asi'},
        "assets_curr_oth": {'eur', 'asi'},
        "bookvalue_ps": {'usa', 'eur', 'asi'},
        "capex": {'usa', 'eur', 'asi'},
        "cash": {'usa', 'eur', 'asi'},
        "cash_st": {'eur', 'asi'},
        "cashflow": {'usa'},
        "cashflow_dividends": {'usa'},
        "cashflow_fin": {'usa', 'eur', 'asi'},
        "cashflow_invst": {'usa', 'eur', 'asi'},
        "cashflow_op": {'usa', 'eur', 'asi'},
        "cogs": {'usa', 'eur', 'asi'},
        "cost_of_revenue": {'eur', 'asi'},
        "current_ratio": {'usa', 'eur', 'asi'},
        "debt": {'usa', 'eur', 'asi'},
        "debt_lt": {'usa', 'eur', 'asi'},
        "debt_lt_curr": {'eur', 'asi'},
        "debt_st": {'usa', 'eur', 'asi'},
        "depre": {'eur', 'asi'},
        "depre_amort": {'usa', 'eur', 'asi'},
        "ebit": {'usa', 'eur', 'asi'},
        "ebitda": {'usa', 'eur', 'asi'},
        "employee": {'usa', 'eur'},
        "enterprise_value": {'usa', 'eur'},
        "eps": {'usa', 'eur', 'asi'},
        "equity": {'usa', 'eur', 'asi'},
        "goodwill": {'usa', 'eur', 'asi'},
        "income": {'usa', 'eur', 'asi'},
        "income_beforeextra": {'usa', 'eur', 'asi'},
        "income_tax": {'usa', 'eur', 'asi'},
        "income_tax_payable": {'usa', 'eur', 'asi'},
        "interest_expense": {'usa', 'eur', 'asi'},
        "inventory": {'usa', 'eur', 'asi'},
        "inventory_turnover": {'usa', 'eur', 'asi'},
        "invested_capital": {'usa', 'eur', 'asi'},
        "liabilities": {'usa', 'eur', 'asi'},
        "liabilities_cur_oth": {'eur', 'asi'},
        "liabilities_curr": {'usa', 'eur', 'asi'},
        "liabilities_oth": {'eur', 'asi'},
        "operating_expense": {'usa', 'eur', 'asi'},
        "operating_income": {'usa', 'eur', 'asi'},
        "operating_margin": {'eur', 'asi'},
        "ppent": {'usa', 'eur', 'asi'},
        "ppent_net": {'eur', 'asi'},
        "preferred_dividends": {'eur', 'asi'},
        "pretax_income": {'usa', 'eur', 'asi'},
        "quick_ratio": {'eur', 'asi'},
        "rd_expense": {'usa'},
        "receivable": {'usa', 'eur', 'asi'},
        "retained_earnings": {'usa', 'eur', 'asi'},
        "return_assets": {'usa', 'eur', 'asi'},
        "return_equity": {'usa', 'eur', 'asi'},
        "revenue": {'usa', 'eur', 'asi'},
        "sales": {'usa', 'eur', 'asi'},
        "sales_growth": {'usa'},
        "sales_ps": {'usa'},
        "SGA_expense": {'usa', 'eur', 'asi'},
        "working_capital": {'usa'}
    },
    "ANALYST_ESTIMATE_DATA": {
        "est_bookvalue_ps": {'usa'},
        "est_capex": {'usa'},
        "est_cashflow_fin": {'usa'},
        "est_cashflow_invst": {'usa'},
        "est_cashflow_op": {'usa'},
        "est_cashflow_ps": {'usa'},
        "est_dividend_ps": {'usa'},
        "est_ebit": {'usa'},
        "est_ebitda": {'usa'},
        "est_eps": {'usa'},
        "est_epsa": {'usa'},
        "est_epsr": {'usa'},
        "est_fcf": {'usa'},
        "est_fcf_ps": {'usa'},
        "est_ffo": {'usa'},
        "est_ffoa": {'usa'},
        "est_grossincome": {'usa'},
        "est_netdebt": {'usa'},
        "est_netprofit": {'usa'},
        "est_netprofit_adj": {'usa'},
        "est_ptp": {'usa'},
        "est_ptpr": {'usa'},
        "est_rd_expense": {'usa'},
        "est_sales": {'usa'},
        "est_sga": {'usa'},
        "est_shequity": {'usa'},
        "est_rbv_ps": {'usa'},
        "est_tot_assets": {'usa'},
        "est_tot_goodwill": {'usa'},
        "etz_eps": {'usa'},
        "etz_eps_delta": {'usa'},
        "etz_eps_ret": {'usa'},
        "etz_eps_tsrank": {'usa'},
        "etz_revenue": {'usa'},
        "etz_revenue_delta": {'usa'},
        "etz_revenue_ret": {'usa'}
    },
    "RELATIONSHIP_DATA": {
        "rel_num_all": {'usa'},
        "rel_num_comp": {'usa'},
        "rel_num_cust": {'usa'},
        "rel_num_part": {'usa'},
        "rel_ret_all": {'usa'},
        "rel_ret_comp": {'usa'},
        "rel_ret_cust": {'usa'},
        "rel_ret_part": {'usa'}
    },
    "SENTIMENT_DATA": {
        "snt_bearish": {'usa'},
        "snt_bearish_tsrank": {'usa'},
        "snt_bullish": {'usa'},
        "snt_bullish_tsrank": {'usa'},
        "snt_buzz": {'usa'},
        "snt_buzz_bfl": {'usa'},
        "snt_buzz_ret": {'usa'},
        "snt_ratio": {'usa'},
        "snt_ratio_tsrank": {'usa'},
        "snt_social_value": {'usa'},
        "snt_social_volume": {'usa'},
        "snt_value": {'usa'}
    },
    "US_NEWS_DATA": {
        "news_prev_vol": {'usa'},
        "news_curr_vol": {'usa'},
        "news_mov_vol": {'usa'},
        "news_ratio_vol": {'usa'},
        "news_open_vol": {'usa'},
        "news_close_vol": {'usa'},
        "news_tot_ticks": {'usa'},
        "news_atr14": {'usa'},
        "news_prev_day_ret": {'usa'},
        "news_prev_close": {'usa'},
        "news_open": {'usa'},
        "news_open_gap": {'usa'},
        "news_spy_last": {'usa'},
        "news_ton_high": {'usa'},
        "news_ton_low": {'usa'},
        "news_ton_last": {'usa'},
        "news_eod_high": {'usa'},
        "news_eod_low": {'usa'},
        "news_spy_close": {'usa'},
        "news_post_vwap": {'usa'},
        "news_pre_vwap": {'usa'},
        "news_main_vwap": {'usa'},
        "news_all_vwap": {'usa'},
        "news_eod_vwap": {'usa'},
        "news_max_up_amt": {'usa'},
        "news_max_up_ret": {'usa'},
        "news_max_dn_amt": {'usa'},
        "news_max_dn_ret": {'usa'},
        "news_session_range": {'usa'},
        "news_session_range_pct": {'usa'},
        "news_ls": {'usa'},
        "news_indx_perf": {'usa'},
        "news_pct_30sec": {'usa'},
        "news_pct_1min": {'usa'},
        "news_pct_5_min": {'usa'},
        "news_pct_10min": {'usa'},
        "news_pct_30min": {'usa'},
        "news_pct_60min": {'usa'},
        "news_pct_90min": {'usa'},
        "news_pct_120min": {'usa'},
        "news_mins_1_pct_up": {'usa'},
        "news_mins_2_pct_up": {'usa'},
        "news_mins_3_pct_up": {'usa'},
        "news_mins_4_pct_up": {'usa'},
        "news_mins_5_pct_dn": {'usa'},
        "news_mins_7_5_pct_dn": {'usa'},
        "news_mins_10_pct_dn": {'usa'},
        "news_mins_20_pct_dn": {'usa'},
        "news_mins_1_chg": {'usa'},
        "news_mins_2_chg": {'usa'},
        "news_mins_3_chg": {'usa'},
        "news_mins_4_chg": {'usa'},
        "news_mins_5_chg": {'usa'},
        "news_mins_7_5_chg": {'usa'},
        "news_mins_10_chg": {'usa'},
        "news_mins_20_chg": {'usa'},
        'news_cap': {'usa'},
        "news_pe_ratio": {'usa'},
        "news_dividend_yield": {'usa'},
        "news_short_interest": {'usa'},
        "news_high_exc_stddev": {'usa'},
        "news_low_exc_stddev": {'usa'},
        "news_vol_stddev": {'usa'},
        "news_range_stddev": {'usa'},
        "news_atr_ratio": {'usa'},
        "news_eps_actual": {'usa'}
    },
    "PERFORMANCE_METRICS_DATA": {
        "qs_ir_x": {'usa'},
        "qs_sharpe_x": {'usa'},
        "qs_sortino_ratio_x": {'usa'},
        "qs_treynor_ratio_x": {'usa'},
        "qs_gain_loss_var_ratio_x": {'usa'},
        "qs_gain_var_x": {'usa'},
        "qs_loss_var_x": {'usa'},
        "qs_exp_shortfall_95ci_x": {'usa'},
        "qs_exp_shortfall_99ci_x": {'usa'},
        "qs_mod_sharpe_95ci_x": {'usa'},
        "qs_mod_sharpe_99ci_x": {'usa'},
        "qs_rachev_ratio_95ci_x": {'usa'},
        "qs_rachev_ratio_99ci_x": {'usa'},
        "qs_starr_ratio_95ci_x": {'usa'},
        "qs_starr_ratio_99ci_x": {'usa'},
        "qs_var_95ci_x": {'usa'},
        "qs_var_99ci_x": {'usa'}
    },
    "PRICE_TARGET_DATA": {
        "rtk_ptg_high": {'usa'},
        "rtk_ptg_low": {'usa'},
        "rtk_ptg_mean": {'usa'},
        "rtk_ptg_median": {'usa'},
        "rtk_ptg_stddev": {'usa'},
        "rtg_ptg_number": {'usa'}
    },
    "VOLATILITY_AND_RISK_FACTOR_DATA": {
        "qs_alpha_1d": {'usa'},
        "qs_beta_1d": {'usa'},
        "qs_fdim_1d": {'usa'},
        "qs_hurst_1d": {'usa'},
        "qs_kurt_1d": {'usa'},
        "qs_mom3_1d": {'usa'},
        "qs_mom4_1d": {'usa'},
        "qs_ret_1d": {'usa'},
        "qs_skew_1d": {'usa'},
        "qs_var_1d": {'usa'},
        "qs_alpha_5d": {'usa'},
        "qs_beta_5d": {'usa'},
        "qs_fdim_5d": {'usa'},
        "qs_hurst_5d": {'usa'},
        "qs_kurt_5d": {'usa'},
        "qs_mom3_5d": {'usa'},
        "qs_mom4_5d": {'usa'},
        "qs_ret_5d": {'usa'},
        "qs_skew_5d": {'usa'},
        "qs_var_5d": {'usa'},
        "qs_alpha_22d": {'usa'},
        "qs_beta_22d": {'usa'},
        "qs_fdim_22d": {'usa'},
        "qs_hurst_22d": {'usa'},
        "qs_kurt_22d": {'usa'},
        "qs_mom3_22d": {'usa'},
        "qs_mom4_22d": {'usa'},
        "qs_ret_22d": {'usa'},
        "qs_skew_22d": {'usa'},
        "qs_var_22d": {'usa'},
    },
    "EBITDA_ESTIMATE_MODEL": {
        "star_ebitda_analyst_number_fq1": {'usa', 'eur', 'asi'},
        "star_ebitda_fq1_enddate": {'usa', 'eur', 'asi'},
        "star_ebitda_surprise_prediction_fq1": {'usa', 'eur', 'asi'},
        "star_ebitda_smart_estimate_fq1": {'usa', 'eur', 'asi'},
        "star_ebitda_analyst_number_fq2": {'usa', 'eur', 'asi'},
        "star_ebitda_fq2_enddate": {'usa', 'eur', 'asi'},
        "star_ebitda_surprise_prediction_fq2": {'usa', 'eur', 'asi'},
        "star_ebitda_smart_estimate_fq2": {'usa', 'eur', 'asi'},
        "star_ebitda_analyst_number_fy1": {'usa', 'eur', 'asi'},
        "star_ebitda_fy1_enddate": {'usa', 'eur', 'asi'},
        "star_ebitda_surprise_prediction_fy1": {'usa', 'eur', 'asi'},
        "star_ebitda_smart_estimate_fy1": {'usa', 'eur', 'asi'},
        "star_ebitda_analyst_number_fy2": {'usa', 'eur', 'asi'},
        "star_ebitda_fy2_enddate": {'usa', 'eur', 'asi'},
        "star_ebitda_surprise_prediction_fy2": {'usa', 'eur', 'asi'},
        "star_ebitda_smart_estimate_fy2": {'usa', 'eur', 'asi'},
        "star_ebitda_analyst_number_12m": {'usa', 'eur', 'asi'},
        "star_ebitda_12m_enddate": {'usa', 'eur', 'asi'},
        "star_ebitda_surprise_prediction_12m": {'usa', 'eur', 'asi'},
        "star_ebitda_smart_estimate_12m": {'usa', 'eur', 'asi'},
    },
    "GROWTH_VALUATION_MODEL": {
        "star_val_dividend_projection_fy1": {'usa', 'eur', 'asi'},
        "star_val_dividend_projection_fy2": {'usa', 'eur', 'asi'},
        "star_val_dividend_projection_fy3": {'usa', 'eur', 'asi'},
        "star_val_dividend_projection_fy4": {'usa', 'eur', 'asi'},
        "star_val_dividend_projection_fy5": {'usa', 'eur', 'asi'},
        "star_val_dividend_projection_fy6": {'usa', 'eur', 'asi'},
        "star_val_dividend_projection_fy7": {'usa', 'eur', 'asi'},
        "star_val_dividend_projection_fy8": {'usa', 'eur', 'asi'},
        "star_val_dividend_projection_fy9": {'usa', 'eur', 'asi'},
        "star_val_dividend_projection_fy10": {'usa', 'eur', 'asi'},
        "star_val_dividend_projection_fy11": {'usa', 'eur', 'asi'},
        "star_val_dividend_projection_fy12": {'usa', 'eur', 'asi'},
        "star_val_dividend_projection_fy13": {'usa', 'eur', 'asi'},
        "star_val_dividend_projection_fy14": {'usa', 'eur', 'asi'},
        "star_val_dividend_projection_fy15": {'usa', 'eur', 'asi'},
        "star_val_earnings_measure_type": {'usa', 'eur', 'asi'},
        "star_val_earnings_projection_fy1": {'usa', 'eur', 'asi'},
        "star_val_earnings_projection_fy2": {'usa', 'eur', 'asi'},
        "star_val_earnings_projection_fy3": {'usa', 'eur', 'asi'},
        "star_val_earnings_projection_fy4": {'usa', 'eur', 'asi'},
        "star_val_earnings_projection_fy5": {'usa', 'eur', 'asi'},
        "star_val_earnings_projection_fy6": {'usa', 'eur', 'asi'},
        "star_val_earnings_projection_fy7": {'usa', 'eur', 'asi'},
        "star_val_earnings_projection_fy8": {'usa', 'eur', 'asi'},
        "star_val_earnings_projection_fy9": {'usa', 'eur', 'asi'},
        "star_val_earnings_projection_fy10": {'usa', 'eur', 'asi'},
        "star_val_earnings_projection_fy11": {'usa', 'eur', 'asi'},
        "star_val_earnings_projection_fy12": {'usa', 'eur', 'asi'},
        "star_val_earnings_projection_fy13": {'usa', 'eur', 'asi'},
        "star_val_earnings_projection_fy14": {'usa', 'eur', 'asi'},
        "star_val_earnings_projection_fy15": {'usa', 'eur', 'asi'},
        "star_val_fwd10_eps_cagr": {'usa', 'eur', 'asi'},
        "star_val_fwd5_eps_cagr": {'usa', 'eur', 'asi'},
        "star_val_fy_end_date": {'usa', 'eur', 'asi'},
        "star_val_implied10_eps_cagr": {'usa', 'eur', 'asi'},
        "star_val_implied5_eps_cagr": {'usa', 'eur', 'asi'},
        "star_val_iv_projection": {'usa', 'eur', 'asi'},
        "star_val_piv_ratio": {'usa', 'eur', 'asi'},
        "star_val_piv_industry_rank": {'usa', 'eur', 'asi'},
        "star_val_piv_region_rank": {'usa', 'eur', 'asi'},
        "star_val_piv_sector_rank": {'usa', 'eur', 'asi'},
        "star_val_buyback_yield": {'usa', 'eur', 'asi'},
        "star_val_dividend_yield": {'usa', 'eur', 'asi'},
        "star_val_ev_sales": {'usa', 'eur', 'asi'},
        "star_val_industry_rank": {'usa', 'eur', 'asi'},
        "star_val_pb": {'usa', 'eur', 'asi'},
        "star_val_pcf": {'usa', 'eur', 'asi'},
        "star_val_pe": {'usa', 'eur', 'asi'},
        "star_val_region_rank": {'usa', 'eur', 'asi'},
        "star_val_sector_rank": {'usa', 'eur', 'asi'}
    },
    "SMART_RATIOS": {
        "star_sr_global_rank": {'usa', 'eur', 'asi'},
        "star_sr_liquidity": {'usa', 'eur', 'asi'},
        "star_sr_region_rank": {'usa', 'eur', 'asi'},
        "star_sr_sector_rank": {'usa', 'eur', 'asi'},
        "star_sr_industr_rank": {'usa', 'eur', 'asi'},
        "star sr_country_rank": {'usa', 'eur', 'asi'},
        "star_sr_growth": {'usa', 'eur', 'asi'},
        "star_sr_profitability": {'usa', 'eur', 'asi'},
        "star_sr_leverage": {'usa', 'eur', 'asi'},
        "star_sr_coverage": {'usa', 'eur', 'asi'}
    },
    "SMART_HOLDINGS": {
        "star_hold_global_change_rank": {'usa', 'eur', 'asi'},
        "star_hold_region_change_rank": {'usa', 'eur', 'asi'},
        "star_hold_country_rank": {'usa', 'eur', 'asi'},
        "star_hold_global_rank": {'usa', 'eur', 'asi'},
        "star_hold_industry_rank": {'usa', 'eur', 'asi'},
        "star_hold_global_owner_rank": {'usa', 'eur', 'asi'},
        "star_hold_region_owner_rank": {'usa', 'eur', 'asi'},
        "star_hold_region_rank": {'usa', 'eur', 'asi'},
        "star_hold_global_screening_rank": {'usa', 'eur', 'asi'},
        "star_hold_region_screening_rank": {'usa', 'eur', 'asi'},
        "star_hold_sector_rank": {'usa', 'eur', 'asi'}
    },
    "INSIDER_MODEL": {
        "star_in_country_rank": {'usa'},
        "star_in_industry_rank": {'usa'},
        "star_in_sector_rank": {'usa'},
        "star_in_netbuyer_ratio_rank": {'usa'},
        "star_in_purchase_depth_rank": {'usa'},
        "star_in_selling_depth_rank": {'usa'}
    },
    "EPS_ESTIMATE_MODEL": {
        "star_eps_analyst_number_fq1": {'usa', 'eur', 'asi'},
        "star_eps_fq1_enddate": {'usa', 'eur', 'asi'},
        "star_eps_surprise_prediction_fq1": {'usa', 'eur', 'asi'},
        "star_eps_smart_estimate_fq1": {'usa', 'eur', 'asi'},
        "star_eps_analyst_number_fq2": {'usa', 'eur', 'asi'},
        "star_eps_fq2_enddate": {'usa', 'eur', 'asi'},
        "star_eps_surprise_prediction_fq2": {'usa', 'eur', 'asi'},
        "star_eps_smart_estimate_fq2": {'usa', 'eur', 'asi'},
        "star_eps_analyst_number_fy1": {'usa', 'eur', 'asi'},
        "star_eps_fy1_enddate": {'usa', 'eur', 'asi'},
        "star_eps_surprise_prediction_fy1": {'usa', 'eur', 'asi'},
        "star_eps_smart_estimate_fy1": {'usa', 'eur', 'asi'},
        "star_eps_analyst_number_fy2": {'usa', 'eur', 'asi'},
        "star_eps_fy2_enddate": {'usa', 'eur', 'asi'},
        "star_eps_surprise_prediction_fy2": {'usa', 'eur', 'asi'},
        "star_eps_smart_estimate_fy2": {'usa', 'eur', 'asi'},
        "star_eps_analyst_number_12m": {'usa', 'eur', 'asi'},
        "star_eps_12m_enddate": {'usa', 'eur', 'asi'},
        "star_eps_surprise_prediction_12m": {'usa', 'eur', 'asi'},
        "star_eps_smart_estimate_12m": {'usa', 'eur', 'asi'},
    },
    "CREDIT_RISK_MODEL": {
        "star_ccr_country_rank": {'usa', 'eur', 'asi'},
        "star_ccr_global_rank": {'usa', 'eur', 'asi'},
        "star_ccr_implied_rating": {'usa', 'eur', 'asi'},
        "star_ccr_industry_rank": {'usa', 'eur', 'asi'},
        "star_ccr_combined_pd": {'usa', 'eur', 'asi'},
        "star_ccr_region_rank": {'usa', 'eur', 'asi'},
        "star_ccr_sector_rank": {'usa', 'eur', 'asi'}
    },
    "PRICE_MOMENTUM_MODEL": {
        "star_pm_global_rank": {'usa', 'eur', 'asi'},
        "star_pm_industry": {'usa', 'eur', 'asi'},
        "star_pm_longterm": {'usa', 'eur', 'asi'},
        "star_pm_midterm": {'usa', 'eur', 'asi'},
        "star_pm_region_rank": {'usa', 'eur', 'asi'},
        "star_pm_shortterm": {'usa', 'eur', 'asi'}
    },
    "REVENUE_ESTIMATE_MODEL": {
        "star_rev_analyst_number_fq1": {'usa', 'eur', 'asi'},
        "star_rev_analyst_number_fq2": {'usa', 'eur', 'asi'},
        "star_rev_analyst_number_fy1": {'usa', 'eur', 'asi'},
        "star_rev_analyst_number_fy2": {'usa', 'eur', 'asi'},
        "star_rev_fq1_enddate": {'usa', 'eur', 'asi'},
        "star_rev_fq2_enddate": {'usa', 'eur', 'asi'},
        "star_rev_fy1_enddate": {'usa', 'eur', 'asi'},
        "star_rev_fy2_enddate": {'usa', 'eur', 'asi'},
        "star_rev_surprise_prediction_12m": {'usa', 'eur', 'asi'},
        "star_rev_surprise_prediction_fq1": {'usa', 'eur', 'asi'},
        "star_rev_surprise_prediction_fq2": {'usa', 'eur', 'asi'},
        "star_rev_surprise_prediction_fy1": {'usa', 'eur', 'asi'},
        "star_rev_surprise_prediction_fy2": {'usa', 'eur', 'asi'},
        "star_rev_smart_estimate_12m": {'usa', 'eur', 'asi'},
        "star_rev_smart_estimate_fq1": {'usa', 'eur', 'asi'},
        "star_rev_smart_estimate_fq2": {'usa', 'eur', 'asi'},
        "star_rev_smart_estimate_fy1": {'usa', 'eur', 'asi'},
        "star_rev_smart_estimate_fy2": {'usa', 'eur', 'asi'}
    },
    "ANALYST_REVISIONS": {
        "star_arm_score": {'usa', 'eur', 'asi'},
        "star_arm_score_5": {'usa', 'eur', 'asi'},
        "star_arm_global_rank": {'usa', 'eur', 'asi'},
        "star_arm_country_rank": {'usa', 'eur', 'asi'},
        "star_arm_pref_earnings_score": {'usa', 'eur', 'asi'},
        "star_arm_recommendations_score": {'usa', 'eur', 'asi'},
        "star_arm_revenue_score": {'usa', 'eur', 'asi'},
        "star_arm_secondary_earnings_score": {'usa', 'eur', 'asi'},
        "star_arm_score_change_1m": {'usa', 'eur', 'asi'},
        "star_arm_region_rank_decimal": {'usa', 'eur', 'asi'},
        "star_arm_rec_change_flag": {'usa', 'eur', 'asi'},
        "star_arm_rec_days_since_2lv_change": {'usa', 'eur', 'asi'},
        "star_arm_rec_days_since_new": {'usa', 'eur', 'asi'},
        "star_arm_rec_days_since_newsell": {'usa', 'eur', 'asi'},
        "star_arm_rec_ndown_30": {'usa', 'eur', 'asi'},
        "star_arm_rec_nup_30": {'usa', 'eur', 'asi'},
        "star_arm_rec_mean_change30": {'usa', 'eur', 'asi'},
        "star_arm_rec_mean_prior7": {'usa', 'eur', 'asi'}
    },
    "SHORT_INTEREST_MODEL": {
        "star_si_insown_pct": {'usa'},
        "star_si_country_rank": {'usa'},
        "star_si_cap_rank": {'usa'},
        "star_si_sector_rank": {'usa'},
        "star_si_country_rank_unadj": {'usa'},
        "star_si_shortsqueeze_rank": {'usa'}
    },
    "STREET_EVENTS": {
        "se_event_count": {'usa'},
        "se_neg_words": {'usa'},
        "se_pos_words": {'usa'},
        "se_neg_score": {'usa'},
        "se_pos_score": {'usa'},
        "se_score": {'usa'}
    },
    "OPTIONS_ANALYTICS": {
        "pcr_oi_all": {'usa'},
        "pcr_vol_all": {'usa'},
        "call_breakeven_10": {'usa'},
        "forward_price_10": {'usa'},
        "option_breakeven_10": {'usa'},
        "pcr_oi_10": {'usa'},
        "pcr_vol_10": {'usa'},
        "put_breakeven_10": {'usa'},
        "call_breakeven_20": {'usa'},
        "forward_price_20": {'usa'},
        "option_breakeven_20": {'usa'},
        "pcr_oi_20": {'usa'},
        "pcr_vol_20": {'usa'},
        "put_breakeven_20": {'usa'},
        "call_breakeven_30": {'usa'},
        "forward_price_30": {'usa'},
        "option_breakeven_30": {'usa'},
        "pcr_oi_30": {'usa'},
        "pcr_vol_30": {'usa'},
        "put_breakeven_30": {'usa'},
        "call_breakeven_60": {'usa'},
        "forward_price_60": {'usa'},
        "option_breakeven_60": {'usa'},
        "pcr_oi_60": {'usa'},
        "pcr_vol_60": {'usa'},
        "put_breakeven_60": {'usa'},
        "call_breakeven_90": {'usa'},
        "forward_price_90": {'usa'},
        "option_breakeven_90": {'usa'},
        "pcr_oi_90": {'usa'},
        "pcr_vol_90": {'usa'},
        "put_breakeven_90": {'usa'},
        "call_breakeven_120": {'usa'},
        "forward_price_120": {'usa'},
        "option_breakeven_120": {'usa'},
        "pcr_oi_120": {'usa'},
        "pcr_vol_120": {'usa'},
        "put_breakeven_120": {'usa'},
        "call_breakeven_150": {'usa'},
        "forward_price_150": {'usa'},
        "option_breakeven_150": {'usa'},
        "pcr_oi_150": {'usa'},
        "pcr_vol_150": {'usa'},
        "put_breakeven_150": {'usa'},
        "call_breakeven_180": {'usa'},
        "forward_price_180": {'usa'},
        "option_breakeven_180": {'usa'},
        "pcr_oi_180": {'usa'},
        "pcr_vol_180": {'usa'},
        "put_breakeven_180": {'usa'},
        "call_breakeven_270": {'usa'},
        "forward_price_270": {'usa'},
        "option_breakeven_270": {'usa'},
        "pcr_oi_270": {'usa'},
        "pcr_vol_270": {'usa'},
        "put_breakeven_270": {'usa'},
        "call_breakeven_360": {'usa'},
        "forward_price_360": {'usa'},
        "option_breakeven_360": {'usa'},
        "pcr_oi_360": {'usa'},
        "pcr_vol_360": {'usa'},
        "put_breakeven_360": {'usa'},
        "call_breakeven_720": {'usa'},
        "forward_price_720": {'usa'},
        "option_breakeven_720": {'usa'},
        "pcr_oi_720": {'usa'},
        "pcr_vol_720": {'usa'},
        "put_breakeven_720": {'usa'},
        "call_breakeven_1080": {'usa'},
        "forward_price_1080": {'usa'},
        "option_breakeven_1080": {'usa'},
        "pcr_oi_1080": {'usa'},
        "pcr_vol_1080": {'usa'},
        "put_breakeven_1080": {'usa'},
    },
    "SYSTEMATIC_RISK_METRICS": {
        "beta_last_30_days_spy": {'usa'},
        "correlation_last_30_days_spy": {'usa'},
        "systematic_risk_last_30_days": {'usa'},
        "unsystematic_risk_last_30_days": {'usa'},
        "beta_last_60_days_spy": {'usa'},
        "correlation_last_60_days_spy": {'usa'},
        "systematic_risk_last_60_days": {'usa'},
        "unsystematic_risk_last_60_days": {'usa'},
        "beta_last_90_days_spy": {'usa'},
        "correlation_last_90_days_spy": {'usa'},
        "systematic_risk_last_90_days": {'usa'},
        "unsystematic_risk_last_90_days": {'usa'},
        "beta_last_360_days_spy": {'usa'},
        "correlation_last_360_days_spy": {'usa'},
        "systematic_risk_last_360_days": {'usa'},
        "unsystematic_risk_last_360_days": {'usa'},
    },
    "STOCK_REPORTS_PLUS": {
        "srp_average_score": {'usa', 'eur', 'asi'},
        "srp_earnings_score": {'usa', 'eur', 'asi'},
        "srp_fundamental_score": {'usa', 'eur', 'asi'},
        "srp_insider_trading_score": {'usa', 'eur', 'asi'},
        "srp_price_momentum_score": {'usa', 'eur', 'asi'},
        "srp_relative_valuation_score": {'usa', 'eur', 'asi'},
        "srp_risk_score": {'usa', 'eur', 'asi'}
    },
    "VOLATILITY_DATA": {
        "historical_volatility_10": {'usa'},
        "implied_volatility_call_10": {'usa'},
        "implied_volatility_mean_10": {'usa'},
        "implied_volatility_mean_skew_10": {'usa'},
        "implied_volatility_put_10": {'usa'},
        "parkinson_volatility_10": {'usa'},
        "historical_volatility_20": {'usa'},
        "implied_volatility_call_20": {'usa'},
        "implied_volatility_mean_20": {'usa'},
        "implied_volatility_mean_skew_20": {'usa'},
        "implied_volatility_put_20": {'usa'},
        "parkinson_volatility_20": {'usa'},
        "historical_volatility_30": {'usa'},
        "implied_volatility_call_30": {'usa'},
        "implied_volatility_mean_30": {'usa'},
        "implied_volatility_mean_skew_30": {'usa'},
        "implied_volatility_put_30": {'usa'},
        "parkinson_volatility_30": {'usa'},
        "historical_volatility_60": {'usa'},
        "implied_volatility_call_60": {'usa'},
        "implied_volatility_mean_60": {'usa'},
        "implied_volatility_mean_skew_60": {'usa'},
        "implied_volatility_put_60": {'usa'},
        "parkinson_volatility_60": {'usa'},
        "historical_volatility_90": {'usa'},
        "implied_volatility_call_90": {'usa'},
        "implied_volatility_mean_90": {'usa'},
        "implied_volatility_mean_skew_90": {'usa'},
        "implied_volatility_put_90": {'usa'},
        "parkinson_volatility_90": {'usa'},
        "historical_volatility_120": {'usa'},
        "implied_volatility_call_120": {'usa'},
        "implied_volatility_mean_120": {'usa'},
        "implied_volatility_mean_skew_120": {'usa'},
        "implied_volatility_put_120": {'usa'},
        "parkinson_volatility_120": {'usa'},
        "historical_volatility_150": {'usa'},
        "implied_volatility_call_150": {'usa'},
        "implied_volatility_mean_150": {'usa'},
        "implied_volatility_mean_skew_150": {'usa'},
        "implied_volatility_put_150": {'usa'},
        "parkinson_volatility_150": {'usa'},
        "historical_volatility_180": {'usa'},
        "implied_volatility_call_180": {'usa'},
        "implied_volatility_mean_180": {'usa'},
        "implied_volatility_mean_skew_180": {'usa'},
        "implied_volatility_put_180": {'usa'},
        "parkinson_volatility_180": {'usa'},
        "implied_volatility_call_270": {'usa'},
        "implied_volatility_mean_270": {'usa'},
        "implied_volatility_mean_skew_270": {'usa'},
        "implied_volatility_put_270": {'usa'},
        "implied_volatility_call_360": {'usa'},
        "implied_volatility_mean_360": {'usa'},
        "implied_volatility_mean_skew_360": {'usa'},
        "implied_volatility_put_360": {'usa'},
        "implied_volatility_call_720": {'usa'},
        "implied_volatility_mean_720": {'usa'},
        "implied_volatility_mean_skew_720": {'usa'},
        "implied_volatility_put_720": {'usa'},
        "implied_volatility_call_1080": {'usa'},
        "implied_volatility_mean_1080": {'usa'},
        "implied_volatility_mean_skew_1080": {'usa'},
        "implied_volatility_put_1080": {'usa'},
    },
    "MODEL_RATINGS_DATA": {
        "rating": {'usa'}
    },
    "MODEL_DATA": {
        "mdf_cap": {'usa'},
        "mdf_fnl": {'usa'},
        "mdf_inv_q": {'usa'},
        "mdf_nqi": {'usa'},
        "mdf_pay_q": {'usa'},
        "mdf_pfd": {'usa'},
        "mdf_pmo": {'usa'},
        "mdf_sti_q": {'usa'},
        "mdf_cex_q": {'usa'},
        "mdf_cfa_q": {'usa'},
        "mdf_cfi_q": {'usa'},
        "mdf_com": {'usa'},
        "mdf_cse": {'usa'},
        "mdf_dep": {'usa'},
        "mdf_dep_q": {'usa'},
        "mdf_fii": {'usa'},
        "mdf_ite_q": {'usa'},
        "mdf_mfq": {'usa'},
        "mdf_pay": {'usa'},
        "mdf_pbk": {'usa'},
        "mdf_peg": {'usa'},
        "mdf_per": {'usa'},
        "mdf_pfd_q": {'usa'},
        "mdf_ppe_q": {'usa'},
        "mdf_prm": {'usa'},
        "mdf_pva": {'usa'},
        "mdf_pvr": {'usa'},
        "mdf_rcv": {'usa'},
        "mdf_rcv_q": {'usa'},
        "mdf_rev": {'usa'},
        "mdf_rte_q": {'usa'},
        "mdf_sal": {'usa'},
        "mdf_shr": {'usa'},
        "mdf_sph": {'usa'},
        "mdf_spm": {'usa'},
        "mdf_std": {'usa'},
        "mdf_std_q": {'usa'},
        "mdf_sti": {'usa'},
        "mdf_tax": {'usa'},
        "mdf_tca_q": {'usa'},
        "mdf_trr": {'usa'},
        "mdf_val": {'usa'},
        "mdf_vmo": {'usa'},
        "mdf_bso": {'usa'},
        "mdf_bso_q": {'usa'},
        "mdf_ceq": {'usa'},
        "mdf_cex": {'usa'},
        "mdf_cfi": {'usa'},
        "mdf_cse_q": {'usa'},
        "mdf_das": {'usa'},
        "mdf_ebt": {'usa'},
        "mdf_ebt_q": {'usa'},
        "mdf_eda": {'usa'},
        "mdf_emo": {'usa'},
        "mdf_eup": {'usa'},
        "mdf_gpr": {'usa'},
        "mdf_ibt": {'usa'},
        "mdf_ibt_q": {'usa'},
        "mdf_iex_q": {'usa'},
        "mdf_inv": {'usa'},
        "mdf_ita": {'usa'},
        "mdf_ite": {'usa'},
        "mdf_mci": {'usa'},
        "mdf_nco_q": {'usa'},
        "mdf_net": {'usa'},
        "mdf_net_q": {'usa'},
        "mdf_oin": {'usa'},
        "mdf_oin_q": {'usa'},
        "mdf_pcf": {'usa'},
        "mdf_peh": {'usa'},
        "mdf_plc": {'usa'},
        "mdf_rec": {'usa'},
        "mdf_roi": {'usa'},
        "mdf_rte": {'usa'},
        "mdf_sci": {'usa'},
        "mdf_sed": {'usa'},
        "mdf_sga": {'usa'},
        "mdf_smo": {'usa'},
        "mdf_tcl_q": {'usa'},
        "mdf_ato": {'usa'},
        "mdf_bsd": {'usa'},
        "mdf_cne": {'usa'},
        "mdf_csh_q": {'usa'},
        "mdf_isd": {'usa'},
        "mdf_ldf": {'usa'},
        "mdf_mfy": {'usa'},
        "mdf_nco": {'usa'},
        "mdf_rac": {'usa'},
        "mdf_roe": {'usa'},
        "mdf_sdr": {'usa'},
        "mdf_vei": {'usa'},
        "mdf_chi": {'usa'},
        "mdf_eno": {'usa'},
        "mdf_grm": {'usa'},
        "mdf_gro": {'usa'},
        "mdf_gwl_q": {'usa'},
        "mdf_iex": {'usa'},
        "mdf_ito": {'usa'},
        "mdf_idt_q": {'usa'},
        "mdf_odl": {'usa'},
        "mdf_pec": {'usa'},
        "mdf_ppe": {'usa'},
        "mdf_pvh": {'usa'},
        "mdf_rev_q": {'usa'},
        "mdf_cfl": {'usa'},
        "mdf_ebm": {'usa'},
        "mdf_edv": {'usa'},
        "mdf_efy": {'usa'},
        "mdf_gwl": {'usa'},
        "mdf_ltd": {'usa'},
        "mdf_peq": {'usa'},
        "mdf_plb": {'usa'},
        "mdf_tcl": {'usa'},
        "mdf_deq": {'usa'},
        "mdf_grp": {'usa'},
        "mdf_pss": {'usa'},
        "mdf_shb": {'usa'},
        "mdf_avi": {'usa'},
        "mdf_div": {'usa'},
        "mdf_fnd": {'usa'},
        "mdf_inb": {'usa'},
        "mdf_ass": {'usa'},
        "mdf_csh": {'usa'},
        "mdf_grp_q": {'usa'},
        "mdf_ita_q": {'usa'},
        "mdf_qty": {'usa'},
        "mdf_tca": {'usa'},
        "mdf_cps": {'usa'},
        "mdf_dpr": {'usa'},
        "mdf_tie": {'usa'},
        "mdf_coa": {'usa'},
        "mdf_coa_q": {'usa'},
        "mdf_gry": {'usa'},
        "mdf_pre": {'usa'},
        "mdf_exi": {'usa'},
        "mdf_oey": {'usa'},
        "mdf_bsd_q": {'usa'},
        "mdf_ccc_q": {'usa'},
        "mdf_tas_q": {'usa'},
        "mdf_atr": {'usa'},
        "mdf_isd_q": {'usa'},
        "mdf_nps": {'usa'},
        "mdf_era": {'usa'},
        "mdf_pra": {'usa'},
        "mdf_yld": {'usa'},
        "mdf_tli_q": {'usa'},
        "mdf_bkv": {'usa'},
        "mdf_h52": {'usa'},
        "mdf_bta": {'usa'},
        "mdf_pro": {'usa'},
        "mdf_sg3": {'usa'},
        "mdf_pri": {'usa'},
        "mdf_lpe": {'usa'},
        "mdf_opi": {'usa'},
        "mdf_tma": {'usa'},
        "mdf_l52": {'usa'},
        "mdf_alp": {'usa'},
        "mdf_hpv": {'usa'},
        "mdf_hpe": {'usa'},
        "mdf_fma": {'usa'},
        "mdf_dvp": {'usa'},
        "mdf_bet": {'usa'},
        "mdf_sga_q": {'usa'},
        "mdf_rds": {'usa'},
        "mdf_eg5": {'usa'},
        "mdf_f2i": {'usa'},
        "mdf_eg3": {'usa'},
        "mdf_avl": {'usa'},
        "mdf_hdy": {'usa'},
        "mdf_ind": {'usa'},
        "mdf_fdi": {'usa'},
        "mdf_ccr": {'usa'},
        "mdf_eqx": {'usa'},
        "mdf_rnd_q": {'usa'},
        "mdf_rnd": {'usa'},
        "mdf_hdq": {'usa'},
        "mdf_hdg": {'usa'},
        "mdf_fni": {'usa'},
        "mdf_ape": {'usa'},
        "mdf_tas": {'usa'},
        "mdf_dg3": {'usa'},
        "mdf_ref": {'usa'},
        "mdf_qex": {'usa'},
        "mdf_pg1": {'usa'},
        "mdf_pg3": {'usa'},
        "mdf_ccc": {'usa'},
        "mdf_roa": {'usa'},
        "mdf_ecu": {'usa'},
        "mdf_hsy": {'usa'},
        "mdf_hsq": {'usa'},
        "mdf_tli": {'usa'},
        "mdf_csp": {'usa'},
        "mdf_hsg": {'usa'},
        "mdf_pgy": {'usa'},
        "mdf_vol": {'usa'},
        "mdf_pgq": {'usa'},
        "mdf_pgw": {'usa'},
        "mdf_pgh": {'usa'},
        "mdf_pgm": {'usa'},
        "mdf_pgn": {'usa'},
        "mdf_pgd": {'usa'},
        "mdg_pgf": {'usa'},
        "mdf_hey": {'usa'},
        "mdf_sqx": {'usa'},
        "mdf_qsx": {'usa'},
        "mdf_heq": {'usa'},
        "mdf_sic": {'usa'},
        "mdf_heg": {'usa'}
    },
    "INSTITUTIONAL_OWNERSHIP_DATA": {
        "io_inst_holding": {'usa'},
        "io_inst_prev_holding": {'usa'},
        "io_inst_mv": {'usa'},
        "io_inst_prev_mv": {'usa'},
        "io_inst_pct": {'usa'},
        "io_inst_number": {'usa'},
        "io_fund_holding": {'usa'},
        "io_fund_prev_holding": {'usa'},
        "io_fund_mv": {'usa'},
        "io_fund_prev_mv": {'usa'},
        "io_fund_pct": {'usa'},
        "io_fund_number": {'usa'}
    }
}


class Recipe(object):
    """
    Базовый класс рецепта.
    Переменные в template это просто именованные значения для функции .format().
    Например, {A} + {B} - две переменные А и B
    """
    def __init__(self, id, template, description="", commutate=True):
        assert isinstance(id, str), "Id must be string HUUUMAN"
        assert isinstance(template, list), "Template must be list HUUUMAN"
        assert isinstance(description, str), "Description must be string HUUUMAN"
        assert isinstance(commutate, bool), "Commutate must be boolean HUUUMAN"
        self.id = id
        self.template = template
        self.commutate = commutate
        self.variables = []
        for row in template:
            self.variables += [i[1] for i in Formatter().parse(row) if i[1]]
        self.description = description

    @property
    def row_template(self):
        res = ""
        for row in self.template:
            res += row + '\n'
        return res

    def _check_db_existance(self, cursor):
        """
        По имени (id) проверяет наличие рецепта в таблице recipes
        :param cursor: объект курсора базы данных mysql
        :return: True если рецепт есть, False иначе
        """
        query = \
            """
            SELECT 1 FROM recipes WHERE id='{id}' 
            """.format(id=self.id)
        cursor.execute(query)
        if cursor.fetchone():
            return True
        else:
            return False

    def to_db(self, cursor):
        """
        Отправляет рецепт (шаблон) в таблицу recipes
        :param cursor: объект курсора базы данных mysql
        :return: True если добавление успешно, False иначе, если рецепт уже был в таблице, то вернёт True
        """
        if not self._check_db_existance(cursor):
            try:
                query = \
                    """
                    INSERT INTO recipes (id, commutate, description, template) VALUES ('{id}', {commutate}, '{description}', '{template}')
                    """.format(id=self.id, commutate=self.commutate, description=self.description, template=self.row_template)
                cursor.execute(query)
                return True
            except Exception as e:
                print(e)
                return False
        else:
            print("This recipe is already in db: {id}".format(id=self.id))
            return True


class Alpha(object):
    """
    Базовый класс Alpha, с объектами класса Alpha работают методы класса Websim
    """

    REGIONS_UNIVERSE = {'USA': ['TOP3000', 'TOP2000', 'TOP1000', 'TOP500', 'TOP200'],
                        'EUR': ['TOP1200', 'TOP800', 'TOP600', 'TOP400', 'TOP100'],
                        'ASI': ['TOP1500', 'TOP1000', 'TOP500', 'TOP150']}

    REGIONS_DELAY = {'USA': ['1', '0'],
                     'EUR': ['1', '0'],
                     'ASI': ['1']}

    NEUTRALIZATIONS = ['None', 'Market', 'Sector', 'Industry', 'Subindustry']

    PASTEURIZE = ['On', 'Off']

    NANHANDLING = ['On', 'Off']

    alpha_stats = ['year', 'booksize', 'long_count', 'short_count', 'pnl', 'sharpe', 'fitness',
                   'returns', 'draw_down', 'turn_over', 'margin']

    stats = {
        'submittable': False,
        'submitted': False,
        'classified': 'INFERIOR',
        'year_by_year': []
    }

    ASSOCIATED_DB_TABLE = 'alphas'
    ASSOCIATED_STATS_DB_TABLE = 'alphas_stats'

    def __init__(self, region, universe, delay, decay, max_stock_weight, neutralization, pasteurize, nanhandling, text, components=[]):
        assert isinstance(region, str), 'Region of the alpha must be simple string HUUUMAN'
        assert isinstance(universe, str), 'Universe of the alpha must be simple string HUUUMAN'
        assert isinstance(text, list), 'Text of the alpha must be list HUUUMAN'
        assert isinstance(delay, int), 'Delay of the alpha must be simple integer HUUUMAN'
        assert isinstance(decay, int), 'Delay of the alpha must be simple integer HUUUMAN'
        assert isinstance(max_stock_weight, float) or isinstance(max_stock_weight, int), 'Max stock weight of the alpha must be simple float or integer like 0 HUUUMAN'
        assert isinstance(neutralization, str), 'Neutralization of the alpha must be simple string HUUUMAN'
        assert isinstance(pasteurize, str), 'Pasteurize must be simple str HUUUMAN'
        assert isinstance(nanhandling, str), 'Nanhandling must be simple str HUUUMAN'
        assert isinstance(components, list), 'Components must be list type HUUUMAN'

        if region.upper() in Alpha.REGIONS_UNIVERSE:
            self.region = region.upper()
            if universe.upper() in Alpha.REGIONS_UNIVERSE[self.region]:
                self.universe = universe.upper()
            else:
                raise ValueError("Got unexpected universe value: {}. Possible values for chosen region are {}".format(
                    universe.upper(), str(Alpha.REGIONS_UNIVERSE[self.region])))
        else:
            raise ValueError('Got unexpected region value: {}. Possible values are {}'.format(region.upper(), str(
                list(Alpha.REGIONS_UNIVERSE.keys()))))
        new_text = []
        for elem in text:
            new_text.append(elem.lower())
        self.text = new_text
        if str(delay) in Alpha.REGIONS_DELAY[self.region]:
            self.delay = delay
        else:
            raise ValueError("Got unexpected delay value: {}. Possible values are {}".format(delay, str(
                Alpha.REGIONS_DELAY[self.region])))
        self.decay = decay
        if max_stock_weight >= 0.0:
            self.max_stock_weight = max_stock_weight
        else:
            raise ValueError(
                "Got unexpected max_stock_weight value: {}. Max stock value must be greater or equal than zero".format(
                    max_stock_weight))

        neutralization = neutralization.capitalize()
        if neutralization in Alpha.NEUTRALIZATIONS:
            self.neutralization = neutralization
        else:
            raise ValueError("Got unexpected neutralization value: {}. Possible values are {}".format(neutralization,
                                                                                                      str(
                                                                                                          Alpha.NEUTRALIZATIONS)))

        pasteurize = pasteurize.capitalize()
        if pasteurize in Alpha.PASTEURIZE:
            self.pasteurize = pasteurize
        else:
            raise ValueError("Got unexpected pasteurize value: {}. Possible values are {}".format(pasteurize, str(Alpha.PASTEURIZE)))

        nanhandling = nanhandling.capitalize()
        if nanhandling in Alpha.NANHANDLING:
            self.nanhandling = nanhandling
        else:
            raise ValueError("Got unexpected nanhandling value: {}. Possible values are {}".format(nanhandling, str(Alpha.NANHANDLING)))

        self.simulated = False
        if components:
            self.components = components
        else:
            self.components = []

        if not self._check_correctness():
            raise ValueError("This alpha is not valid for such universe, region, delay options")

    def print_stats(self):
        """
        Красиво выводит статы альфы
        :return: None
        """
        for k, v in self.stats.items():
            print(k, v)

    @property
    def text_str(self):
        """
        Представление текста альфы как строчки (вместо массива)
        :return: строка - текст альфы
        """
        res = ""
        for elem in self.text:
            res += elem + '  \n'
        return res

    @property
    def hash(self):
        """
        md5 хэш альфы, nuff said
        ЛУЧШЕ ВОТ ЭТО ВОТ ВООБЩЕ БОЛЬШЕ НЕ ТРОГАТЬ
        :return: hexdigest md5
        пример:
        In [6]: md5('123'.encode('utf-8')).hexdigest()
        Out[6]: '202cb962ac59075b964b07152d234b70'
        """
        return md5(
            (str(self.region) +
             str(self.universe) +
             str(self.text) +
             str(self.delay) +
             str(self.decay) +
             str(self.max_stock_weight) +
             str(self.neutralization) +
             str(self.pasteurize) +
             str(self.nanhandling)).encode('utf-8')
        ).hexdigest()

    def _check_db_existance(self, cursor):
        """
        Производит проверку наличия альфы по хэшу в таблице alphas
        :param cursor: объект курсора базы mysql
        :return: True, если альфа есть в таблице alphas, False иначе
        """
        query = \
            """
            SELECT 1 FROM alphas WHERE md5hash='{md5hash}'
            """.format(md5hash=self.hash)
        cursor.execute(query)
        if cursor.fetchone():
            return True
        else:
            return False

    def to_json_str(self):
        d = dict(
            text=self.text,
            region=self.region,
            universe=self.universe,
            decay=self.decay,
            delay=self.delay,
            max_stock_weight=self.max_stock_weight,
            neutralization=self.neutralization,
            pasteurize=self.pasteurize,
            nanhandling=self.nanhandling
        )
        return json.dumps(d)

    def to_db(self, cursor, recipe):
        """
        Отправляет все данные связанные с альфой в базу данных.

        Логика следующая. Альфа в любом случае должна быть просимулирована.
        При вызове сначала проверяется присутствие альфы в базе.
        Если альфы в базе нет, то производится вставка в таблицы alphas и alphas_stats,
        если же альфа уже есть в базе, то в случае если в self.stats['submitted'] выставлено True, произойдет вызов sql
        запроса Update, который выставит флаг submitted в базе в True, если же self.stats['submitted'] False, то ничего
        не произойдёт и вернётся True.
        Обратите внимание, что если несколько раз вызывать to_db на альфе с self.stats['submitted'] True, то будет
        перезаписываться время сабмита (submitted_time).
        :param cursor: объект курсора базы mysql
        :param recipe: объект класса Recipe
        :return: True если удалось вставить альфу в таблицу, False иначе, при этом если запись уже была, вернётся True
        """
        if self.simulated:
            if not self._check_db_existance(cursor):
                try:
                    query = \
                        """
                        INSERT INTO {table} (md5hash, author, submittable, submitted, classified, recipe_id, components, skeleton) 
                        VALUES ('{md5hash}', '{author}', {submittable}, {submitted}, '{classified}', '{recipe_id}', '{components}', '{skeleton}')
                        """.format(table=Alpha.ASSOCIATED_DB_TABLE,
                                   md5hash=self.hash,
                                   author=config.DB_USER,
                                   submittable=self.stats['submittable'],
                                   submitted=self.stats['submitted'],
                                   classified=self.stats['classified'],
                                   recipe_id=recipe.id,
                                   components=json.dumps(self.components),
                                   skeleton=self.to_json_str()
                                   )
                    if self.stats['submitted']:
                        query = \
                            """
                            INSERT INTO {table} (md5hash, author, submittable, submitted, classified, submitted_time, recipe_id, components, skeleton) 
                            VALUES ('{md5hash}', '{author}', {submittable}, {submitted}, '{classified}', '{submitted_time}', '{recipe_id}', '{components}', '{skeleton}')
                            """.format(table=Alpha.ASSOCIATED_DB_TABLE,
                                       md5hash=self.hash,
                                       author=config.DB_USER,
                                       submittable=self.stats['submittable'],
                                       submitted=self.stats['submitted'],
                                       classified=self.stats['classified'],
                                       submitted_time=datetime.datetime.now(),
                                       recipe_id=recipe.id,
                                       components=json.dumps(self.components),
                                       skeleton=self.to_json_str()
                                       )
                    cursor.execute(query)

                    query = \
                    """
                    SELECT id FROM {table} WHERE md5hash='{md5hash}'
                    """.format(table=Alpha.ASSOCIATED_DB_TABLE, md5hash=self.hash)
                    cursor.execute(query)
                    d = cursor.fetchone()
                    alpha_id = None
                    if d:
                        alpha_id = d[0]
                    else:
                        raise Exception("Couldn't find inserted alpha")

                    for stat in self.stats['year_by_year']:
                        query = \
                        """
                        INSERT INTO {table} (alpha_id, year, fitness, returns, sharpe, long_count, short_count, margin, turn_over, draw_down, booksize, pnl, left_corr, right_corr)
                        VALUES ({alpha_id}, '{year}', {fitness}, {returns}, {sharpe}, {long_count}, {short_count}, {margin}, {turn_over}, {draw_down}, {booksize}, {pnl}, {left_corr}, {right_corr})
                        """.format(table=Alpha.ASSOCIATED_STATS_DB_TABLE,
                                   alpha_id=alpha_id,
                                   year=stat['year'],
                                   fitness=stat['fitness'],
                                   returns=stat['returns'][:-1],
                                   sharpe=stat['sharpe'],
                                   long_count=stat['long_count'],
                                   short_count=stat['short_count'],
                                   margin=stat['margin'][:-3],
                                   turn_over=stat['turn_over'][:-1],
                                   draw_down=stat['draw_down'][:-1],
                                   booksize=stat['booksize'][:-1],
                                   pnl=stat['pnl'][:-1],
                                   left_corr=self.stats['left_corr'],
                                   right_corr=self.stats['right_corr'])
                        cursor.execute(query)
                    return True
                except Exception as e:
                    print(e)
                    return False
            else:
                print("This alpha is already in db")
                if self.stats['submitted']:
                    print("Now it's submitted, updating field, submitted_time")
                    try:
                        query = \
                        """
                        UPDATE {table}
                        SET submitted_time='{submitted_time}'
                        WHERE md5hash='{md5hash}'
                        """.format(table=Alpha.ASSOCIATED_DB_TABLE,
                                   submitted_time=datetime.datetime.now(),
                                   md5hash=self.hash)
                        cursor.execute(query)
                    except Exception as e:
                        print(e)
                        return False
                return True
        else:
            print("Simulate alpha before inserting it to db!")
            return False

    def __str__(self):
        return \
            """
            Alpha object:
            {text}
            {region}
            {universe}
            {delay}
            {decay}
            {max_stock_weight}
            {neutralization}
            {pasteurize}
            {nanhandling}
            """.format(
                region=self.region,
                universe=self.universe,
                text=self.text,
                delay=self.delay,
                decay=self.decay,
                max_stock_weight=self.max_stock_weight,
                neutralization=self.neutralization,
                pasteurize=self.pasteurize,
                nanhandling=self.nanhandling
            )

    def pretty_print_text(self):
        for row in self.text:
            print(row)

    def _return_variables_and_special_words(self, variables_flag=True, other_words_flag=True, grouping_words_flag=True, operator_words_flag=True, data_words_flag=True):
        variables_list = []
        special_words_list = []
        other_words_list = []
        grouping_words_list = []
        operator_words_list = []
        data_words_list = []
        for row in self.text:
            for word in re.findall(r'\b[a-zA-Z_]+[0-9_]*[a-zA-Z_]*\b', row): # допускает такие переменные как x, alpha2b, alpha_2b
                word_lower = word.lower()
                found = False
                if other_words_flag:
                    if word_lower in OTHER_WORDS.keys():
                        found = True
                        other_words_list.append(word)

                if grouping_words_flag:
                    if word_lower in GROUPING_WORDS.keys():
                        found = True
                        grouping_words_list.append(word)

                if operator_words_flag:
                    if word_lower in OPERATOR_WORDS:
                        found = True
                        operator_words_list.append(word)

                if data_words_flag:
                    for key, value in DATA_WORDS.items():
                        if word_lower in value.keys():
                            found = True
                            data_words_list.append(word)
                            break

                if variables_flag:
                    if not found:
                        variables_list.append(word)

        special_words_list = other_words_list + grouping_words_list + operator_words_list + data_words_list

        return variables_list, special_words_list

    def _check_correctness(self):
        variables, specials = self._return_variables_and_special_words(other_words_flag=False, grouping_words_flag=False, operator_words_flag=False)
        import pymysql
        with pymysql.connect(config.DB_HOST, config.DB_USER, config.DB_USER_PASSWORD, config.DB_NAME) as cursor:
            for word in specials:
                query = \
                """
                    SELECT 
                      1 
                    FROM 
                      data_words
                    WHERE
                      data_name='{data_name}'
                      AND 
                      region='{region}'
                      AND 
                      delay={delay}
                """.format(
                    data_name=word.lower(),
                    region=self.region.lower(),
                    delay=self.delay
                )
                cursor.execute(query)
                if not cursor.fetchone():
                    print("found incompaitable with {} {} {} special word '{}'".format(self.universe.lower(), self.region.lower(), self.delay, word))
                    return False

        return True

    def obfuscate_text(self, suffix):
        variables_list, specials = self._return_variables_and_special_words()
        result = self.text.copy()
        for var in variables_list:
            regex = re.compile(r'\b{}\b'.format(var))

            tmp = []
            for row in result:
                tmp.append(re.sub(regex, var+suffix, row))

            result = tmp

        return result


class Actions(ActionChains):
    def wait(self, time_s: float):
        self._actions.append(lambda: time.sleep(time_s))
        return self


class WebSim(object):
    """
    Базовый класс вебсим, через него взаимодействуем с сайтом wq
    """
    def __init__(self, implicitly_wait=120):

        self.logger = logging.getLogger(self.__class__.__name__)
        try:
            os.makedirs('../logs/')
        except OSError:
            pass
        hdlr = logging.FileHandler('../logs/{}.log'.format(self.__class__.__name__))
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.INFO)

        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1366x768')
        self.driver = webdriver.Chrome(chrome_options=options,
                                       executable_path=config.CHROMEDRIVER_PATH)
        self.implicitly_wait = implicitly_wait
        self.driver.implicitly_wait(
            implicitly_wait)  # будет ждать implicitly_wait секунд появления элемента на странице
        self.date = datetime.datetime.now().__str__().split()[0]
        self.login_time = -1

    def __del__(self):
        """
        Не забываем убивать драйвер (процесс хрома)
        :return: None
        """
        self.driver.quit()

    def login(self, relog=False):
        """
        Данные берутся из конфига
        :param relog: если флаг relog True, то предварительно идёт запрос страницы симуляции, чтобы после логина
        перекинуло куда надо
        :return: True в случае успешного логина, False иначе
        """
        try:
            if relog:
                self.driver.get('https://www.worldquantvrc.com/simulate')

            self.driver.get('https://www.worldquantvrc.com/login')
            try:
                self.driver.implicitly_wait(10)
                self.driver.find_element_by_class_name('cookie-consent-accept').click()
            except Exception:
                print("Already signed cookie")
            self.driver.implicitly_wait(self.implicitly_wait) # setting implicitly wait back
            log_pass = self.driver.find_elements_by_class_name('form-control')
            log_pass[0].clear(), log_pass[0].send_keys(config.EMAIL)
            log_pass[1].clear(), log_pass[1].send_keys(config.PASSWORD)
            log_pass[1].send_keys(Keys.RETURN)

            self.login_time = time.time()
            time.sleep(10)
            print("Login successuful")
            return True
        except Exception as e:
            self.logger.error("Couldn't log in")
            self.logger.error(str(e))
            return False
            # find dashboard element

    def _get_stats(self):
        """
        Возвращает статистику год за годом
        :return: list of dicts
        """
        table = self.driver.find_elements_by_class_name('standard-row')
        stats = []
        for row_id, row in enumerate(table):
            data = row.find_elements_by_tag_name('td')
            stats.append(
                {
                    'year': data[1].text,
                    'booksize': data[2].text,
                    'long_count': data[3].text,
                    'short_count': data[4].text,
                    'pnl': data[5].text,
                    'sharpe': data[6].text,
                    'fitness': data[7].text,
                    'returns': data[8].text,
                    'draw_down': data[9].text,
                    'turn_over': data[10].text,
                    'margin': data[11].text
                }
            )
        return stats

    def simulate_alpha(self, alpha, debug=False):
        """
        Симулирует одну альфу, выставляет настройки, вставляет текст, жмёт на нужные кнопки
        :param alpha: объект класса Alpha
        :return: ничего не возвращает, выкинет исключение в случае ошибки
        """
        assert isinstance(alpha, Alpha), 'alpha must be Alpha class instance'
        alert_message = None
        self.driver.get('https://www.worldquantvrc.com/simulate')
        self.driver.find_element_by_id("test-flowsexprCode").click()  # switching to fast expressions
        alert_container = self.driver.find_element_by_class_name('sim-alert-container')
        try:
            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')
            input_form = self.driver.find_element_by_class_name('CodeMirror-code')
            # TODO: remove CodeMirror events from the input form. It substitutes symbols
            # self.driver.execute_script('''
            #
            # ''', input_form)
            body = self.driver.find_element_by_tag_name('body')
            settings_button = self.driver.find_element_by_class_name('test-settingslink')
            region_select = Select(self.driver.find_element_by_name('region'))
            universe_select = Select(self.driver.find_element_by_name('univid'))
            delay_select = Select(self.driver.find_element_by_name('delay'))
            neutralization_select = Select(self.driver.find_element_by_name('opneut'))
            pasteurize_select = Select(self.driver.find_element_by_name('pasteurize'))
            nanhandling_select = Select(self.driver.find_element_by_name('nanhandling'))
            # backdays_hidden_value = self.driver.find_element_by_name('backdays')  # not visible selector, custom field
            decay_input = self.driver.find_element_by_name('decay')
            max_stock_weight_input = self.driver.find_element_by_name('optrunc')
            sim_action_simulate = self.driver.find_element_by_class_name('sim-action-simulate')

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

            input_form.click() # фокусируемся на поле ввода

            input_action = Actions(self.driver)

            l = len(alpha.text)
            for idx in range(l):
                input_action.send_keys(alpha.text[idx])
                if idx != l-1:
                    input_action.key_down(Keys.LEFT_SHIFT).send_keys(Keys.ENTER).key_up(Keys.LEFT_SHIFT)
                else:
                    input_action.send_keys(Keys.ESCAPE)

            input_action.perform()

            go_to_top = Actions(self.driver)
            go_to_top.click(body)
            go_to_top.send_keys_to_element(body, Keys.CONTROL + Keys.HOME)

            go_to_top.perform()

            go_to_end = Actions(self.driver)
            go_to_end.click(body)
            go_to_end.send_keys_to_element(body, Keys.CONTROL + Keys.END)

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

            self.driver.find_element_by_id("test-flowsexprCode").click()

            settings_button.click()

            region_select.select_by_visible_text(alpha.region)

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

            universe_select.select_by_visible_text(alpha.universe)

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

            delay_select.select_by_visible_text(str(alpha.delay))

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

            neutralization_select.select_by_visible_text(alpha.neutralization)

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

            pasteurize_select.select_by_visible_text(alpha.pasteurize)

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now()) + '.png')

            nanhandling_select.select_by_visible_text(alpha.nanhandling)

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now()) + '.png')

            decay_input.clear()
            decay_input.send_keys(str(alpha.decay))

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

            max_stock_weight_input.clear()
            max_stock_weight_input.send_keys(str(alpha.max_stock_weight))
            """
            # no lookback for fast expressions
            self.driver.execute_script('''
                var elem = arguments[0];
                var value = arguments[1];
                elem.value = value;
            ''', backdays_hidden_value, "512") # old lookback_days option
            """
            settings_button.click()

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

            go_to_end.perform()

            body.send_keys(Keys.ESCAPE)

            sim_action_simulate.click()
            self.driver.implicitly_wait(300)

            go_to_top.perform()

            test_btn = self.driver.find_element_by_id('test-statsBtn')
            test_btn.click()
            self.driver.implicitly_wait(self.implicitly_wait)

            go_to_top.perform()

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

            classified = self.driver.find_element_by_id('percentileStats').find_element_by_class_name('panel-title').get_attribute('innerText').upper()
            if classified:
                alpha.stats['classified']=classified

            corr_button = self.driver.find_element_by_id('alphaCorrChartButton')
            action_get_corr = ActionChains(self.driver)
            action_get_corr.click(corr_button)
            action_get_corr.perform()

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

            corrs = dict()
            corr_block = self.driver.find_element_by_class_name('highcharts-series')
            corr_rects = corr_block.find_elements_by_tag_name('rect')
            for rect_id, rect in enumerate(corr_rects):
                elem_height = rect.get_attribute('height')
                elem_width = rect.get_attribute('width')
                if (int(elem_height) == 0) and (int(elem_width) == 0):
                    continue
                else:
                    corrs[rect_id] = elem_height

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

            left_corr_index = min(corrs.keys())
            right_corr_index = max(corrs.keys())

            left_corr_value = -1.0 + left_corr_index * 0.1
            right_corr_value = -1.0 + right_corr_index * 0.1 + 0.1

            alpha.stats['year_by_year'] = self._get_stats()
            alpha.stats['left_corr'] = left_corr_value
            alpha.stats['right_corr'] = right_corr_value

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

            """
            Структура столбцов корреляции
            https://s.mail.ru/FAbH/GwQ3NS9VZ
            """

            # self.driver.find_elements_by_class_name('col-xs-4')[2].click() # так можно кликать тоже, обертка над кнопкой
            self.driver.find_element_by_id('resultTabPanel').find_element_by_class_name(
                'menu').find_elements_by_class_name('item')[3].click()

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

            # жмём check submission
            self.driver.find_element_by_id('checkAlphaContainer').click()

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

            go_to_top.perform()

            submittable = alert_container.get_attribute('innerText')
            submittable_flag = False
            if 'success' in submittable.lower():
                submittable_flag = True
            else:
                alert_message = submittable # raise message why it's not submittable

            alpha.stats['submittable'] = submittable_flag
            alpha.stats['submitted'] = False
            alpha.simulated = True

            go_to_top.perform()

            if debug:
                self.driver.save_screenshot(str(datetime.datetime.now())+'.png')

        except NoSuchElementException as err:
            print("Something went wrong...")
            alert_message = alert_container.get_attribute('innerText').replace(' ', '')
            if not alert_message:
                if debug:
                    self.driver.save_screenshot(str(datetime.datetime.now())+'.png')
                if not self._error(err):
                    print("Couldn't login again, it can be serious issue, stopping...")
                    exit(str(err))

        if debug:
            self.driver.save_screenshot(str(datetime.datetime.now()) + '.png')

        return alert_message

    def submit_alpha(self, alpha):
        """
        Сабмитит альфу. Предполагается, что браузер уже находится на вкладке с кнопкой submit
        :param alpha: объект класса Alpha. Только что просимулированная альфа
        :return: True если альфа засабмитилась, False иначе.
        Также выставляет флаг submitted в словаре stats
        """
        assert isinstance(alpha, Alpha), 'alpha must be Alpha class instance'
        if alpha.stats['submittable']:
            self.driver.find_element_by_id('submitAlphaContainer').click()
            submittable = self.driver.find_element_by_class_name('sim-alert-container').find_element_by_class_name('alert-1').find_element_by_class_name('content').text
            if 'success' in submittable.lower():
                alpha.stats['submitted'] = True
            else:
                alpha.stats['submitted'] = False
            return alpha.stats['submitted']

    def _error(self, error):
        """
        :param error: Объект ошибки
        :return: Возвращает True, если элемент удалось дождаться и произошел успешный перелогин,
        если перелогиниться не удалось, то возвращает False
        """
        if 'CodeMirror-line' in error.msg:
            self.driver.get('https://www.worldquantvrc.com/simulate')
            try:
                element_present = EC.presence_of_element_located((By.CLASS_NAME, 'CodeMirror-line'))
                WebDriverWait(self.driver, 120).until(element_present)
                # WebDriverWait(self.driver, 120).until(element_present).click()
                return True

            except TimeoutException:
                return self.login(relog=True)

        if 'test-statsBtn' in error.msg:
            try:
                element_present = EC.presence_of_element_located((By.ID, 'test-statsBtn'))
                WebDriverWait(self.driver, 180).until(element_present)
                # WebDriverWait(self.driver, 180).until(element_present).click()
                return True

            except TimeoutException:
                return self.login(relog=True)
