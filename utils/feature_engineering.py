import Levenshtein

def distance_similarity(s1: str, s2: str):
    return Levenshtein.ratio(s1, s2)

def convert_to_vector(entry: object, reference: object):
    title_entry = entry["title"]
    title_reference = reference["title"]
    author_entry = entry["authors"]
    author_reference = reference["authors"]
    year_entry = entry["year"]
    year_reference = reference["year"]
    title_distance = distance_similarity(title_entry, title_reference)
    author_entry = distance_similarity(author_entry, author_reference)

    year = 0
    if year_entry == year_reference:
        year = 1
    return [title_distance, author_entry, year]

def khong_biet_dat_ten_gi(entry_array: list[list[object]], reference_array: list[list[object]], cite_to_arkiv: dict):
    vector_train = []
    ground_truth = []
    object_file = {}
    
    for i in range(len(entry_array)):
        file_path = None
        object_entry = {}
        for entry in entry_array[i]:
            entry_name = entry['cite_key']
            entry_array = []
            for reference in reference_array[i]:
                #Used for prediction
                arkiv_id = reference['arkiv_id']
                vector = convert_to_vector(entry, reference)

                if file_path is None:
                    file_path = entry['path']
                entry_array.append({
                    "arkiv_id": arkiv_id,
                    "vector": vector
                })

                vector_train.append(vector)
                if entry['cite_key'] in cite_to_arkiv:
                    if cite_to_arkiv[entry['cite_key']] == reference['arkiv_id']:
                        ground_truth.append(1)
                    else:
                        ground_truth.append(0)
                else:
                    ground_truth.append(0)
            object_entry[entry_name] = entry_array
        object_file[file_path] = object_entry
    return vector_train, ground_truth, object_file


# entry_array = [[
#     {"cite_key": "AcerbiSzekely2014", "title": "Back-testing expected shortfall", "authors": "Acerbi, C. and Szekely, B.", "year": 2014, "path": "./MockFolder/2306-14523"},
#     {"cite_key": "AcerbiTasche2002", "title": "On the coherence of expected shortfall", "authors": "Acerbi, C. and Tasche, D.", "year": 2002, "path": "./MockFolder/2306-14523"},
#     {"cite_key": "ArducaMunari2023", "title": "Fundamental theorem of asset pricing with acceptable risk in markets with frictions", "authors": "Arduca, M. and Munari, C.", "year": 2023, "path": "./MockFolder/2306-14523"},
#     {"cite_key": "ArtznerDelbaenEberHeath1999", "title": "Coherent measures of risk", "authors": "Artzner, P. and Delbaen, F. and Eber, J.M. and Heath, D.", "year": 1999, "path": "./MockFolder/2306-14523"},
#     {"cite_key": "BarrieuScandolo2015", "title": "Assessing financial model risk", "authors": "Barrieu, P. and Scandolo, G.", "year": 2015, "path": "2306-14523"},
#     {"cite_key": "BaselII", "title": "Amendment to the capital accord to incorporate market risks", "authors": "Basel Committee on Banking Supervision", "year": 1996, "path": "2306-14523"},
#     {"cite_key": "BaselIII", "title": "Fundamental review of the trading book", "authors": "Basel Committee on Banking Supervision", "year": 2012, "path": "2306-14523"},
#     {"cite_key": "BaselIIIb", "title": "Risk-based capital requirements", "authors": "Basel Committee on Banking Supervision", "year": 2023, "path": "2306-14523"},
#     {"cite_key": "BertsimasLaupreteSamarov2004", "title": "Shortfall as a risk measure: properties, optimization and applications", "authors": "Bertsimas, D. and Lauprete, G.J. and Samarov, A.", "year": 2004, "path": "2306-14523"},
#     {"cite_key": "BignozziBurzoniMunari2020", "title": "Risk measures based on benchmark loss distributions", "authors": "Bignozzi, V. and Burzoni, M. and Munari, C.", "year": 2020, "path": "2306-14523"},
#     {"cite_key": "BurzoniMunariWang2022", "title": "Adjusted expected shortfall", "authors": "Burzoni, M. and Munari, C. and Wang, R.", "year": 2022, "path": "2306-14523"},
#     {"cite_key": "Cherny2008", "title": "Pricing with coherent risk", "authors": "Cherny, A.", "year": 2008, "path": "2306-14523"},
#     {"cite_key": "ContDeguestScandolo2010", "title": "Robustness and sensitivity analysis of risk measurement procedures", "authors": "Cont, R. and Deguest, R. and Scandolo, G.", "year": 2010, "path": "2306-14523"},
#     {"cite_key": "Delbaen2002", "title": "Coherent risk measures on general probability spaces", "authors": "Delbaen, F.", "year": 2002, "path": "2306-14523"},
#     {"cite_key": "EmbrechtsWang2015", "title": "Seven proofs for the subadditivity of expected shortfall", "authors": "Embrechts, P. and Wang, R.", "year": 2015, "path": "2306-14523"},
#     {"cite_key": "SolvencyII", "title": "Directive 2009/138/EC", "authors": "European Parliament", "year": 2009, "path": "2306-14523"},
#     {"cite_key": "SST", "title": "Technical document on the Swiss Solvency Test", "authors": "Federal Office of Private Insurance", "year": 2006, "path": "2306-14523"},
#     {"cite_key": "FoellmerSchied2002", "title": "Stochastic finance: an introduction in discrete time", "authors": "Föllmer, H. and Schied, A.", "year": 2002, "path": "2306-14523"},
#     {"cite_key": "HerdegenKhan2022", "title": "Mean-portfolio selection and ρ-arbitrage for coherent risk measures", "authors": "Herdegen, M. and Khan, N.", "year": 2022, "path": "2306-14523"},
#     {"cite_key": "RiskMetrics", "title": "RiskMetrics – technical document", "authors": "J.P. Morgan / Reuters", "year": 1996, "path": "2306-14523"},
#     {"cite_key": "KochMunari2016", "title": "Unexpected shortfalls of expected shortfall: extreme default profiles and regulatory arbitrage", "authors": "Koch-Medina, P. and Munari, C.", "year": 2016, "path": "2306-14523"},
#     {"cite_key": "KraetschmerSchiedZaehle2014", "title": "Comparative and qualitative robustness for law-invariant risk measures", "authors": "Krätschmer, V. and Schied, A. and Zähle, H.", "year": 2014, "path": "2306-14523"},
#     {"cite_key": "Kusuoka2001", "title": "On law invariant coherent risk measures", "authors": "Kusuoka, S.", "year": 2001, "path": "2306-14523"},
#     {"cite_key": "MadanCherny2010", "title": "Markets as a counterparty: an introduction to conic finance", "authors": "Madan, D. and Cherny, A.", "year": 2010, "path": "2306-14523"},
#     {"cite_key": "MaoWang2020", "title": "Risk aversion in regulatory capital principles", "authors": "Mao, T. and Wang, R.", "year": 2020, "path": "2306-14523"},
#     {"cite_key": "MunariWeberWilhelmy2022", "title": "Capital requirements and claims recovery: a new perspective on solvency regulation", "authors": "Munari, C. and Weber, S. and Wilhelmy, L.", "year": 2022, "path": "2306-14523"},
#     {"cite_key": "Pflug2000", "title": "Some remarks on the value-at-risk and the conditional value-at-risk", "authors": "Pflug, G.Ch.", "year": 2000, "path": "2306-14523"},
#     {"cite_key": "PflugRoemisch2007", "title": "Modeling, measuring and managing risk", "authors": "Pflug, G.Ch. and Römisch, W.", "year": 2007, "path": "2306-14523"},
#     {"cite_key": "PflugRuszczynski2005", "title": "Measuring risk for income streams", "authors": "Pflug, G.Ch. and Ruszczyński, A.", "year": 2005, "path": "2306-14523"},
#     {"cite_key": "Rockafellar1974", "title": "Conjugate duality and optimization", "authors": "Rockafellar, R.T.", "year": 1974, "path": "2306-14523"},
#     {"cite_key": "RockafellarUryasev2000", "title": "Optimization of conditional value-at-risk", "authors": "Rockafellar, R.T. and Uryasev, S.", "year": 2000, "path": "2306-14523"},
#     {"cite_key": "RockafellarUryasev2002", "title": "Conditional value-at-risk for general loss distributions", "authors": "Rockafellar, R.T. and Uryasev, S.", "year": 2002, "path": "2306-14523"},
#     {"cite_key": "RuszczynskiShapiro2006", "title": "Optimization of risk measures", "authors": "Ruszczyński, A. and Shapiro, A.", "year": 2006, "path": "2306-14523"},
#     {"cite_key": "WangZitikis2021", "title": "An axiomatic foundation for the expected shortfall", "authors": "Wang, R. and Zitikis, R.", "year": 2021, "path": "2306-14523"},
#     {"cite_key": "Weber2018", "title": "Solvency II, or how to sweep the downside risk under the carpet", "authors": "Weber, S.", "year": 2018, "path": "2306-14523"},
#     {"cite_key": "YamaiYoshiba2005", "title": "Value-at-risk versus expected shortfall: a practical perspective", "authors": "Yamai, Y. and Yoshiba, T.", "year": 2005, "path": "2306-14523"},
#     {"cite_key": "Zalinescu2002", "title": "Convex analysis in general vector spaces", "authors": "Zălinescu, C.", "year": 2002, "path": "2306-14523"},
#     {"cite_key": "Ziegel2016", "title": "Coherence and elicitability", "authors": "Ziegel, J.F.", "year": 2016, "path": "2306-14523"}
# ]]

# reference_array = [[
#     {"arkiv_id": "2012-08351", "title": "Fundamental theorem of asset pricing with acceptable risk in markets with frictions", "authors": "Maria Arduca and Cosimo Munari", "year": 2023},
#     {"arkiv_id": "1204.2458", "title": "Comparative and qualitative robustness for law-invariant risk measures", "authors": "Volker Krätschmer and Alexander Schied and Henryk Zähle", "year": 2014},
#     {"arkiv_id": "1702-08901", "title": "Solvency II, or How to Sweep the Downside Risk Under the Carpet", "authors": "Stefan Weber", "year": 2018},
#     {"arkiv_id": "2009-05498", "title": "Mean-ρ portfolio selection and ρ-arbitrage for coherent risk measures", "authors": "Martin Herdegen and Nazem Khan", "year": 2022},
#     {"arkiv_id": "1303.1690", "title": "Coherence and elicitability", "authors": "Johanna F. Ziegel", "year": 2016},
#     {"arkiv_id": "1307.0684", "title": "Assessing Financial Model Risk", "authors": "Pauline Barrieu and Giacomo Scandolo", "year": 2015},
#     {"arkiv_id": "2007-08829", "title": "Adjusted Expected Shortfall", "authors": "Matteo Burzoni and Cosimo Munari and Ruodu Wang", "year": 2022},
#     {"arkiv_id": "2107-10635", "title": "Capital Requirements and Claims Recovery: A New Perspective on Solvency Regulation", "authors": "Cosimo Munari and Lutz Wilhelmy and Stefan Weber", "year": 2022},
#     {"arkiv_id": "math/0605049", "title": "Pricing with coherent risk", "authors": "Alexander S. Cherny", "year": 2008}
# ]]
# cite_to_arkiv = {
#     "ArducaMunari2023": "2012-08351",
#     "BarrieuScandolo2015": "1307.0684",
#     "BurzoniMunariWang2022": "2007-08829",
#     "Cherny2008": "math/0605049",
#     "HerdegenKhan2022": "2009-05498",
#     "KraetschmerSchiedZaehle2014": "1204.2458",
#     "MunariWeberWilhelmy2022": "2107-10635",
#     "Weber2018": "1702-08901",
#     "Ziegel2016": "1303.1690"
# }
# vector_valid, ground_truth_valid, cite_arkiv_valid = khong_biet_dat_ten_gi(entry_array, reference_array, cite_to_arkiv)
# vector_test, ground_truth_test, cite_arkiv_test = khong_biet_dat_ten_gi(entry_array, reference_array, cite_to_arkiv)