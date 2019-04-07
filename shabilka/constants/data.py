# coding=utf-8
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
