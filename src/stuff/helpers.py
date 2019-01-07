# coding=utf-8
import argparse
import json

import itertools

from websim import Alpha, Recipe


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
    "INSTITUTIONAL_OWNERSHIP_DATA": {1}
}

RESERVED_WORDS = {
    "OTHER": {
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
        "subindustry": {'usa', 'eur', 'asi'},
    },
    "GROUPING": {
        "market": {'usa', 'eur', 'asi'},
        "country": {'usa', 'eur', 'asi'},
        "exchange": {'usa', 'eur', 'asi'},
        "sector": {'usa', 'eur', 'asi'},
        "industry": {'usa', 'eur', 'asi'},
        "subindustry": {'usa', 'eur', 'asi'}
    },
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
        "EBIT": {'usa', 'eur', 'asi'},
        "EBITDA": {'usa', 'eur', 'asi'},
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
    "ANALYST_REVISIONS": {
        "star_arm_rec_change_flag": {'usa', 'eur', 'asi'},
        "star_arm_rec_days_since_2lv_change": {'usa', 'eur', 'asi'},
        "star_arm_rec_days_since_new": {'usa', 'eur', 'asi'},
        "star_arm_rec_days_since_newsell": {'usa', 'eur', 'asi'},
        "star_arm_rec_ndown_30": {'usa', 'eur', 'asi'},
        "star_arm_rec_nup_30": {'usa', 'eur', 'asi'},
        "star_arm_rec_mean_change30": {'usa', 'eur', 'asi'},
        "star_arm_rec_mean_prior7": {'usa', 'eur', 'asi'}
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

    }
}


def return_dict_combinations(d):
    assert isinstance(d, dict), "You should pass dictionary to init this object"
    allNames = sorted(d)
    combinations = itertools.product(*(d[name] for name in allNames))
    res = []
    for comb in combinations:
        res.append(zip(allNames, comb))
    return res


class BasicGrinder(object):
    """
    Базовый гриндер.
    Берёт на вход рецепт, массив альф и перебирает всевозможные перестановки (размера количества переменных в
    шаблоне) и параметры "в колесе".
    """
    def __init__(self, recipe, alphas, begin_index=0):
        assert isinstance(recipe, Recipe), "recipe must be Recipe class instance"
        assert isinstance(alphas, list), "alphas must be list"
        for elem in alphas:
            assert isinstance(elem, Alpha), "Each element of the alphas list must be Alpha class instance"
        self.recipe = recipe
        self.alphas = alphas
        self._robin = None
        self.variables_number = len(self.recipe.variables)
        self.begin_index = begin_index
        print("Got {} alphas".format(len(self.alphas)))
        print("Gor recipe {}".format(self.recipe.id))
        print("Number of variables {}".format(self.variables_number))

    def __iter__(self):
        if not self.recipe.commutate:
            self._permutations = itertools.permutations(self.alphas, self.variables_number)
        else:
            self._permutations = itertools.combinations(self.alphas, self.variables_number)
        self._params = [].__iter__()
        self._res = None
        self._idx = 0
        return self

    def _get_next_params(self):
        params_combination = self._params.__next__()
        new_alpha_params_dict = dict(params_combination)
        new_alpha_params_dict['text'] = self._res
        new_alpha_params_dict['components'] = self._current_components
        return new_alpha_params_dict

    def _next(self):
        try:
            new_alpha = Alpha(**self._get_next_params())
            return new_alpha
        except StopIteration:
            print("BasicGrinder: beginning to work with new permutation")
            try:
                alphas_permutation = self._permutations.__next__()
                res = []
                new_vars = []
                params = {
                    'region': [],
                    'universe': [],
                    'decay': [],
                    'delay': [],
                    'max_stock_weight': [],
                    'neutralization': [],
                    'pasteurize': [],
                    'nanhandling': [],
                }
                self._current_components = []
                for idx, alpha in enumerate(alphas_permutation):
                    self._current_components.append(alpha.hash)
                    new_vars.append("var{}".format(idx))
                    old_ending = alpha.text[-1]
                    alpha.text[-1] = alpha.text[-1].replace(';', '')
                    alpha.text[-1] = "var{idx}={alpha_end};".format(idx=idx, alpha_end=alpha.text[-1])
                    res += alpha.text
                    alpha.text[-1] = old_ending
                    for key, val in params.items():
                        attr = getattr(alpha, key)
                        if attr not in val:
                            params[key].append(attr)

                for row in self.recipe.template:
                    res += [row.format(**dict(zip(self.recipe.variables, new_vars)))]
                self._res = res
                print(params)
                self._params = return_dict_combinations(params).__iter__()
                new_alpha = Alpha(**self._get_next_params())
                return new_alpha
            except StopIteration as e:
                print("Permutations ended, stopping")
                raise e
        except ValueError as e:
            print("Incompaitable parameters")
            print(str(e))
            print("Skipping this alpha")
            return self._next()
        except Exception as e:
            print("Caught an exception during iteration. Stopping and writing the last index")
            with open('../logs/' + self.__class__.__name__ + '_stopped_on.log', 'w') as f:
                f.write(str(self._idx))
            raise e

    def __next__(self):
        while self._idx < self.begin_index:
            self._next()
            self._idx += 1
        self._idx += 1
        return self._next()


def read_init(classname):
    def read(filepath):
        module = __import__('websim')
        class_ = getattr(module, classname)

        with open(filepath, 'r') as f:
            records_json = json.load(f)

        res = []
        for record in records_json:
            res.append(class_(**record))

        return res

    return read


read_components = read_init('Alpha') # читалка альф из файла типа components.json
read_recipes = read_init('Recipe') # читалка рецептов из файла типа recipes.json


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def sendemail_via_gmail(gmail_user, gmail_password, to, subject, body):
    assert isinstance(to, list), "to must be list of emails"
    import smtplib

    sent_from = gmail_user

    email_text = """\  
    From: %s  
    To: %s  
    Subject: %s

    %s
    """ % (sent_from, ", ".join(to), subject, body)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, email_text)
        server.close()

        print('Email sent!')
    except:
        print('Something went wrong during email notification sending')

if __name__ == "__main__":
    p = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument('--input', '-i', type=str, help='path to file with alphas', required=True)
    args = p.parse_args()

    filepath = args.input
    alphas_arr = read_components(filepath)
    for elem in alphas_arr:
        print(elem)
