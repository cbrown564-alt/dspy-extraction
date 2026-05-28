# Gan S0 Error Analysis: gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation

## Run

- Artifact directory: `runs\gan_s0_candidate_builder_gap_v1_gpt4_1_mini_full_validation_20260523T170527Z`
- Split: `gan_2026_fixed_v1:validation`
- Analysis scope: `full_split`
- Records in split: 299
- Records analyzed: 299
- Valid scored predictions: 299
- Invalid or missing predictions: 0

## Metrics snapshot (valid predictions only)

| Metric | Accuracy | Correct | Denominator |
| --- | ---: | ---: | ---: |
| normalized_label | 71.2% | 213 | 299 |
| monthly_frequency | 80.6% | 241 | 299 |
| purist_category | 86.0% | 257 | 299 |
| pragmatic_category | 88.6% | 265 | 299 |

Benchmark-facing metrics are monthly frequency, Purist category, and Pragmatic category. Normalized-label exact is diagnostic format fidelity.

## Stratified operational reporting

- All-record denominator: 299 (valid scored: 299; invalid/missing: 0)
- Overall operational failure rate: 19.4% (58 failures)

| Stratum | All records | Valid scored | Operational failure rate | Monthly (valid only) |
| --- | ---: | ---: | ---: | ---: |
| hard_case=true | 39 | 39 | 23.1% | 76.9% |
| hard_case=false | 260 | 260 | 18.8% | 81.2% |
| row_ok=true | 287 | 287 | 20.2% | 79.8% |
| row_ok=false | 12 | 12 | 0.0% | 100.0% |
| gold_pragmatic=frequent | 152 | 152 | 27.6% | 72.4% |
| gold_pragmatic=infrequent | 51 | 51 | 15.7% | 84.3% |
| gold_pragmatic=no_seizure_information | 56 | 56 | 0.0% | 100.0% |
| gold_pragmatic=unknown | 40 | 40 | 20.0% | 80.0% |

## Temporal candidate diagnostics (deterministic scaffold)

These candidates are extracted without model calls and do not change benchmark-facing scoring.
- Gold label present in candidate set: 61/299 (20.4%)

| Record | Gold | Candidates | Gold in candidates |
| --- | --- | --- | --- |
| `gan_14485` | `2 per 3 month` | `2 per 3 month` | yes |
| `gan_6532` | `unknown, multiple per cluster` | — | no |
| `gan_10434` | `multiple cluster per week, 2 to 3 per cluster` | `multiple cluster per week, 2 to 3 per cluster` | yes |
| `gan_4956` | `seizure free for 7 month` | — | no |
| `gan_13123` | `1 per year` | `1 per year` | yes |
| `gan_4702` | `multiple per day` | — | no |
| `gan_10052` | `4 cluster per 3 month, multiple per cluster` | `4 cluster per 3 month, multiple per cluster` | yes |
| `gan_2609` | `1 per day` | — | no |
| `gan_1794` | `8 per 2 month` | — | no |
| `gan_10618` | `unknown, 4 to 6 per cluster` | `unknown, 4 to 6 per cluster` | yes |
| `gan_15306` | `2 to 3 per 15 month` | `2 to 3 per 15 month` | yes |
| `gan_7894` | `seizure free for multiple year` | — | no |
| `gan_3246` | `2 cluster per month, 4 per cluster` | — | no |
| `gan_4113` | `1 per 1 to 2 day` | — | no |
| `gan_14881` | `1 per month` | `1 per month` | yes |
| `gan_536` | `1 per 2 day` | — | no |
| `gan_4709` | `multiple per day` | — | no |
| `gan_9566` | `unknown` | — | no |
| `gan_12679` | `1 per day` | `1 per day` | yes |
| `gan_1584` | `11 per month` | — | no |
| `gan_15997` | `10 per 3 month` | — | no |
| `gan_17287` | `1 per 1 to 2 day` | — | no |
| `gan_16251` | `14 per 4 month` | `14 per 4 month` | yes |
| `gan_16772` | `9 per 5 month` | — | no |
| `gan_16825` | `10 per 6 month` | — | no |
| `gan_12950` | `7 per 3 month` | `7 per 3 month` | yes |
| `gan_10047` | `2 cluster per 3 month, multiple per cluster` | `2 cluster per 3 month, multiple per cluster` | yes |
| `gan_12810` | `5 per 2 month` | `5 per 2 month` | yes |
| `gan_10398` | `1 cluster per week, 2 per cluster` | — | no |
| `gan_16041` | `9 per 3 month` | — | no |
| `gan_714` | `2 per day` | — | no |
| `gan_12465` | `1 per day` | — | no |
| `gan_4011` | `1 per month` | — | no |
| `gan_804` | `1 per month` | — | no |
| `gan_22` | `3 per day` | — | no |
| `gan_16335` | `7 per 3 month` | — | no |
| `gan_3867` | `3 per day` | — | no |
| `gan_15923` | `8 per 2 month` | `8 per 2 month` | yes |
| `gan_467` | `9 per month` | — | no |
| `gan_2513` | `2 to 3 per 2 week` | — | no |
| `gan_10993` | `2 cluster per month, 2 to 4 per cluster` | `2 cluster per month, 2 to 4 per cluster` | yes |
| `gan_14792` | `1 per month` | `1 per month` | yes |
| `gan_13574` | `seizure free for multiple year` | `seizure free for multiple year` | yes |
| `gan_5974` | `unknown` | — | no |
| `gan_6607` | `unknown` | — | no |
| `gan_12438` | `1 per day` | — | no |
| `gan_4597` | `1 per 3 week` | — | no |
| `gan_8564` | `seizure free for 6 month` | — | no |
| `gan_12130` | `multiple per week` | `multiple per week` | yes |
| `gan_731` | `1 per day` | — | no |
| `gan_1914` | `7 per 3 month` | — | no |
| `gan_15639` | `2 per week` | — | no |
| `gan_10583` | `unknown, 2 to 3 per cluster` | — | no |
| `gan_14821` | `1 per month` | `1 per month` | yes |
| `gan_6387` | `unknown` | — | no |
| `gan_10984` | `3 cluster per month, 3 to 4 per cluster` | `3 cluster per month, 3 to 4 per cluster` | yes |
| `gan_8264` | `seizure free for 4 month` | — | no |
| `gan_14250` | `2 per month` | `2 per month` | yes |
| `gan_15876` | `6 per week` | — | no |
| `gan_1463` | `3 per month` | — | no |
| `gan_14689` | `3 per 2 month` | `3 per 2 month` | yes |
| `gan_4100` | `1 per 2 to 3 week` | — | no |
| `gan_15771` | `3 per week` | — | no |
| `gan_9365` | `1 per 2 day` | — | no |
| `gan_198` | `1 per 4 week` | — | no |
| `gan_10003` | `1 cluster per week, multiple per cluster` | `1 cluster per week, multiple per cluster` | yes |
| `gan_16991` | `multiple per month` | — | no |
| `gan_3623` | `7 per week` | — | no |
| `gan_3692` | `9 per week` | — | no |
| `gan_17` | `2 per day` | — | no |
| `gan_10553` | `unknown, 2 to 3 per cluster` | — | no |
| `gan_14002` | `unknown` | — | no |
| `gan_2725` | `1 per 2 week` | — | no |
| `gan_2226` | `3 to 10 per 2 week` | — | no |
| `gan_11380` | `unknown` | — | no |
| `gan_14214` | `2 to 4 per month` | `2 to 4 per month` | yes |
| `gan_3630` | `7 per week` | — | no |
| `gan_16753` | `19 per 6 month` | `19 per 6 month` | yes |
| `gan_12667` | `1 per day` | `1 per day` | yes |
| `gan_15442` | `1 cluster per 4 day, 2 per cluster` | `1 cluster per 4 day, 2 per cluster` | yes |
| `gan_2262` | `7 to 9 per 3 week` | — | no |
| `gan_11408` | `no seizure frequency reference` | — | no |
| `gan_12218` | `1 per day` | — | no |
| `gan_10862` | `1 cluster per week, multiple per cluster` | — | no |
| `gan_11841` | `no seizure frequency reference` | — | no |
| `gan_14628` | `2 per 2 month` | `2 per 2 month` | yes |
| `gan_10996` | `1 to 2 cluster per month, 4 per cluster` | — | no |
| `gan_16938` | `2 per week` | — | no |
| `gan_14081` | `unknown` | — | no |
| `gan_6131` | `unknown` | — | no |
| `gan_10509` | `unknown` | — | no |
| `gan_14354` | `2 to 4 per 3 month` | `2 to 4 per 3 month` | yes |
| `gan_3512` | `unknown` | — | no |
| `gan_11216` | `unknown` | — | no |
| `gan_9424` | `10 per 9 month` | — | no |
| `gan_3225` | `1 cluster per month, 3 to 10 per cluster` | — | no |
| `gan_5976` | `unknown` | — | no |
| `gan_7818` | `seizure free for 2 year` | — | no |
| `gan_13598` | `seizure free for multiple year` | `seizure free for multiple year` | yes |
| `gan_14137` | `unknown` | `unknown` | yes |
| `gan_14973` | `1 per month` | `1 per month` | yes |
| `gan_11044` | `1 cluster per 3 month, 2 to 4 per cluster` | — | no |
| `gan_14040` | `unknown` | — | no |
| `gan_1883` | `4 per 3 month` | — | no |
| `gan_1640` | `5 per week` | — | no |
| `gan_12314` | `3 per week` | — | no |
| `gan_3325` | `3 per week` | — | no |
| `gan_16780` | `3 per 7 month` | — | no |
| `gan_14146` | `unknown` | — | no |
| `gan_12296` | `3 to 4 per day` | — | no |
| `gan_2549` | `7 to 8 per 2 month` | — | no |
| `gan_128` | `17 per month` | — | no |
| `gan_13595` | `seizure free for multiple year` | `seizure free for multiple year` | yes |
| `gan_12145` | `multiple per week` | `multiple per week` | yes |
| `gan_3300` | `9 per month` | — | no |
| `gan_6094` | `3 per month` | — | no |
| `gan_2824` | `1 per day` | — | no |
| `gan_7872` | `seizure free for multiple month` | — | no |
| `gan_1486` | `3 per month` | — | no |
| `gan_7431` | `1 per month` | — | no |
| `gan_11874` | `no seizure frequency reference` | — | no |
| `gan_3095` | `seizure free for 12 month` | — | no |
| `gan_15847` | `6 per week` | — | no |
| `gan_3864` | `3 per day` | — | no |
| `gan_5551` | `multiple per day` | — | no |
| `gan_8160` | `seizure free for multiple month` | — | no |
| `gan_2740` | `1 per month` | — | no |
| `gan_10292` | `unknown` | — | no |
| `gan_12823` | `9 per month` | `9 per month` | yes |
| `gan_338` | `multiple per month` | — | no |
| `gan_12562` | `1 per day` | `1 per day` | yes |
| `gan_10031` | `1 cluster per week, multiple per cluster` | `1 cluster per week, multiple per cluster` | yes |
| `gan_15737` | `2 to 3 per week` | — | no |
| `gan_16883` | `4 per 3 month` | — | no |
| `gan_10447` | `unknown` | — | no |
| `gan_15783` | `2 to 3 per week` | — | no |
| `gan_234` | `1 per 2 month` | — | no |
| `gan_531` | `12 to 30 per 3 month` | — | no |
| `gan_4996` | `seizure free for 16 month` | — | no |
| `gan_3261` | `2 cluster per month, 4 per cluster` | — | no |
| `gan_15513` | `1 cluster per 4 to 5 day, 2 to 3 per cluster` | — | no |
| `gan_16408` | `1 per 3 day` | — | no |
| `gan_2652` | `1 per day` | — | no |
| `gan_6077` | `unknown` | — | no |
| `gan_14655` | `2 per 2 month` | `2 per 2 month` | yes |
| `gan_15404` | `1 cluster per 4 month, 3 to 4 per cluster` | `1 cluster per 4 month, 3 to 4 per cluster` | yes |
| `gan_12871` | `5 per 2 month` | — | no |
| `gan_7882` | `seizure free for 6 month` | — | no |
| `gan_13450` | `seizure free for 1 year` | — | no |
| `gan_31` | `4 per day` | — | no |
| `gan_3113` | `seizure free for 14 month` | — | no |
| `gan_5197` | `seizure free for multiple month` | — | no |
| `gan_12319` | `2 to 3 per week` | — | no |
| `gan_6624` | `unknown` | — | no |
| `gan_4602` | `1 per 7 to 10 day` | — | no |
| `gan_5977` | `unknown` | — | no |
| `gan_11706` | `no seizure frequency reference` | — | no |
| `gan_243` | `1 per 4 month` | — | no |
| `gan_4831` | `seizure free for multiple month` | — | no |
| `gan_9179` | `seizure free for multiple month` | — | no |
| `gan_1070` | `3 to 4 per week` | — | no |
| `gan_17279` | `1 per 4 to 5 week` | — | no |
| `gan_13487` | `seizure free for multiple year` | — | no |
| `gan_8858` | `seizure free for multiple month` | `seizure free for multiple year` | no |
| `gan_8113` | `seizure free for 14 month` | — | no |
| `gan_14965` | `1 per 3 month` | `1 per 3 month` | yes |
| `gan_3747` | `3 per day` | — | no |
| `gan_3329` | `2 to 3 per day` | — | no |
| `gan_2486` | `2 to 3 per 3 month` | — | no |
| `gan_12362` | `2 to 3 per day` | — | no |
| `gan_3355` | `1 per 3 month` | — | no |
| `gan_11434` | `no seizure frequency reference` | — | no |
| `gan_13416` | `seizure free for multiple year` | `1 per day` | no |
| `gan_11196` | `3 cluster per month, 5 per cluster` | — | no |
| `gan_9279` | `1 to 2 per week` | — | no |
| `gan_4700` | `multiple per day` | — | no |
| `gan_13993` | `unknown` | `unknown` | yes |
| `gan_5379` | `seizure free for multiple month` | — | no |
| `gan_15129` | `4 per 15 month` | — | no |
| `gan_12246` | `1 to 2 per day` | — | no |
| `gan_7573` | `1 per 2 week` | — | no |
| `gan_1357` | `1 per day` | — | no |
| `gan_7316` | `1 to 2 per month` | — | no |
| `gan_2795` | `1 per week` | — | no |
| `gan_9063` | `seizure free for 8 month` | — | no |
| `gan_9943` | `1 cluster per 4 to 5 week, multiple per cluster` | — | no |
| `gan_16750` | `6 per 7 month` | `6 per 7 month` | yes |
| `gan_15127` | `5 per 13 month` | `5 per 13 month` | yes |
| `gan_6661` | `0.5 per week` | — | no |
| `gan_5351` | `seizure free for 18 month` | — | no |
| `gan_3791` | `10 per year` | — | no |
| `gan_16523` | `1 per 5 day` | `1 per 5 day` | yes |
| `gan_7884` | `seizure free for multiple month` | — | no |
| `gan_14748` | `2 per 3 month` | `2 per 3 month` | yes |
| `gan_10410` | `1 cluster per week, 3 to 4 per cluster` | `1 cluster per week, 3 to 4 per cluster` | yes |
| `gan_3452` | `6 to 8 per month` | — | no |
| `gan_2781` | `1 per week` | — | no |
| `gan_5682` | `2 to 4 per month` | — | no |
| `gan_4919` | `seizure free for 2 year` | — | no |
| `gan_8577` | `seizure free for multiple month` | — | no |
| `gan_2135` | `unknown` | — | no |
| `gan_14025` | `unknown` | `unknown` | yes |
| `gan_9483` | `8 per 6 month` | — | no |
| `gan_3340` | `2 to 3 per month` | — | no |
| `gan_15255` | `multiple cluster per 15 month, multiple per cluster` | `multiple cluster per 15 month, multiple per cluster` | yes |
| `gan_8852` | `seizure free for 8 month` | — | no |
| `gan_7783` | `seizure free for multiple month` | — | no |
| `gan_11207` | `2 cluster per month, 6 per cluster` | — | no |
| `gan_115` | `7 to 8 per month` | — | no |
| `gan_10673` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | yes |
| `gan_13058` | `2 per 7 month` | `2 per 7 month` | yes |
| `gan_2369` | `3 to 4 per month` | — | no |
| `gan_8224` | `seizure free for multiple month` | — | no |
| `gan_15982` | `9 per 2 month` | — | no |
| `gan_11259` | `unknown` | — | no |
| `gan_744` | `multiple per week` | — | no |
| `gan_4591` | `1 per 5 month` | — | no |
| `gan_14271` | `2 to 3 per month` | `2 to 3 per month` | yes |
| `gan_13290` | `4 per 6 month` | `2 per 6 month` | no |
| `gan_6509` | `1 per week` | — | no |
| `gan_8116` | `seizure free for 12 month` | — | no |
| `gan_16645` | `5 per 7 month` | `5 per 7 month` | yes |
| `gan_3102` | `seizure free for 14 month` | — | no |
| `gan_9002` | `7 per year` | — | no |
| `gan_8474` | `seizure free for multiple month` | — | no |
| `gan_3291` | `9 per month` | — | no |
| `gan_15193` | `multiple per 13 month` | `multiple per 13 month` | yes |
| `gan_16574` | `1 per 4 day` | — | no |
| `gan_4378` | `3 per 2 month` | — | no |
| `gan_6029` | `unknown` | — | no |
| `gan_180` | `1 per 7 day` | — | no |
| `gan_6684` | `3 per 4 month` | — | no |
| `gan_14390` | `2 per 3 month` | `a pair of per 4 month` | no |
| `gan_10751` | `unknown` | — | no |
| `gan_12348` | `2 to 3 per week` | — | no |
| `gan_6296` | `3 per 4 month` | — | no |
| `gan_5092` | `seizure free for multiple month` | — | no |
| `gan_10884` | `1 cluster per week, 3 to 4 per cluster` | — | no |
| `gan_848` | `1 per year` | — | no |
| `gan_16947` | `2 per week` | — | no |
| `gan_11411` | `no seizure frequency reference` | — | no |
| `gan_11221` | `unknown` | — | no |
| `gan_6153` | `9 per month` | — | no |
| `gan_12877` | `10 per 4 month` | `10 per 4 month` | yes |
| `gan_8203` | `seizure free for multiple month` | — | no |
| `gan_1497` | `3 per month` | — | no |
| `gan_17239` | `4 per week` | — | no |
| `gan_182` | `1 per 2 day` | — | no |
| `gan_14036` | `unknown` | `unknown` | yes |
| `gan_7290` | `unknown` | — | no |
| `gan_13019` | `9 per 3 month` | — | no |
| `gan_13376` | `seizure free for 2 year` | — | no |
| `gan_17006` | `2 per week` | — | no |
| `gan_5866` | `4 per 6 week` | — | no |
| `gan_10074` | `5 cluster per month, multiple per cluster` | — | no |
| `gan_750` | `multiple per week` | — | no |
| `gan_14076` | `unknown` | — | no |
| `gan_8844` | `seizure free for 15 month` | — | no |
| `gan_15168` | `multiple per 15 month` | `multiple per 15 month` | yes |
| `gan_3015` | `seizure free for 12 month` | — | no |
| `gan_5653` | `1 per 2 day` | — | no |
| `gan_10542` | `unknown, 2 to 4 per cluster` | — | no |
| `gan_6987` | `unknown` | — | no |
| `gan_8723` | `seizure free for multiple month` | — | no |
| `gan_16529` | `1 per 5 day` | `1 per 5 day` | yes |
| `gan_6763` | `1 per week` | — | no |
| `gan_14092` | `unknown` | — | no |
| `gan_15302` | `1 to 2 per 14 month` | `1 to 2 per 14 month` | yes |
| `gan_5837` | `2 cluster per 3 week, multiple per cluster` | — | no |
| `gan_1694` | `1 cluster per 2 week, 3 per cluster` | — | no |
| `gan_5954` | `2 per week` | — | no |
| `gan_16422` | `1 per 2 to 3 day` | — | no |
| `gan_7341` | `unknown` | — | no |
| `gan_16964` | `2 per week` | — | no |
| `gan_2456` | `6 to 7 per 2 week` | — | no |
| `gan_7420` | `1 to 2 per 2 week` | — | no |
| `gan_2354` | `6 to 7 per week` | — | no |
| `gan_11399` | `unknown` | — | no |
| `gan_11733` | `no seizure frequency reference` | — | no |
| `gan_13149` | `3 per year` | `3 per year` | yes |
| `gan_9109` | `unknown` | — | no |
| `gan_3118` | `seizure free for multiple month` | — | no |
| `gan_11763` | `no seizure frequency reference` | — | no |
| `gan_11748` | `no seizure frequency reference` | — | no |
| `gan_2487` | `2 to 3 per 3 month` | — | no |
| `gan_11804` | `no seizure frequency reference` | — | no |
| `gan_4992` | `seizure free for 11 month` | — | no |
| `gan_2366` | `2 to 4 per year` | — | no |
| `gan_5082` | `seizure free for multiple month` | — | no |
| `gan_9526` | `4 per 8 month` | — | no |
| `gan_8893` | `seizure free for multiple month` | — | no |
| `gan_8645` | `seizure free for multiple month` | — | no |
| `gan_11035` | `1 cluster per 3 month, 1 per cluster` | — | no |
| `gan_8002` | `1 per 6 to 8 week` | — | no |
| `gan_13190` | `1 per 5 month` | `1 per 5 month` | yes |
| `gan_15240` | `multiple cluster per 12 month, multiple per cluster` | `multiple cluster per 12 month, multiple per cluster` | yes |
| `gan_14562` | `3 per 6 month` | `3 per 6 month` | yes |
| `gan_6836` | `1 per week` | — | no |
| `gan_11734` | `no seizure frequency reference` | — | no |

## Do the four metrics move together?

Bit order in patterns is `normalized | monthly | purist | pragmatic` (1 = match).

| Pattern | Label | Count | Share |
| --- | --- | ---: | ---: |
| `1111` | all_four_match | 213 | 71.2% |
| `0111` | monthly_purist_pragmatic_not_normalized | 28 | 9.4% |
| `0001` | pragmatic_only | 8 | 2.7% |
| `0000` | all_four_wrong | 34 | 11.4% |
| `0011` | purist_pragmatic_not_monthly | 16 | 5.4% |

### Logical containment on this run

- Normalized exact (213 records): always co-occurs with monthly, Purist, and Pragmatic match.
- Monthly match (241 records): always implies Purist and Pragmatic; 213 also have normalized exact.
- Purist match (257 records): always implies Pragmatic; 241 also match monthly.
- Pragmatic-only wins (pattern `0001`): 8 records.
- Purist-without-monthly (pattern `0010`/`0011`): 0 + 16 records.

### Boundary cases

- **purist_bin_boundary_within_pragmatic**: 8
- **pragmatic_match_monthly_divergence**: 24
- **purist_match_monthly_divergence**: 16
- **monthly_match_label_surface_mismatch**: 28

## Holistic failure taxonomy

### Action tiers (scored misses)

Benchmark-severe classes should drive prompt or verifier work. Diagnostic-only classes preserve monthly/Purist/Pragmatic matches despite normalized-label mismatch.

| Action tier | Count |
| --- | ---: |
| benchmark_severe | 58 |
| diagnostic_only | 28 |

#### benchmark_severe

| Failure class | Count |
| --- | ---: |
| other_semantic_mismatch | 17 |
| pragmatic_match_monthly_divergence | 16 |
| frequent_undercalled | 7 |
| purist_bin_boundary_within_pragmatic | 7 |
| unknown_as_quantified_rate | 3 |
| cluster_collapsed_to_rate | 2 |
| unknown_as_high_rate | 2 |
| unknown_vs_seizure_free | 2 |
| frequent_overcalled | 1 |
| unknown_vs_no_reference | 1 |

#### diagnostic_only

| Failure class | Count |
| --- | ---: |
| seizure_free_label_shape_mismatch | 15 |
| unknown_cluster_label_shape_mismatch | 5 |
| monthly_match_label_surface_mismatch | 4 |
| seizure_free_to_no_reference_monthly_match | 3 |
| cluster_label_shape_mismatch | 1 |

### Scored misses (normalized label wrong)

| Failure class | Count |
| --- | ---: |
| other_semantic_mismatch | 17 |
| pragmatic_match_monthly_divergence | 16 |
| seizure_free_label_shape_mismatch | 15 |
| purist_bin_boundary_within_pragmatic | 7 |
| frequent_undercalled | 7 |
| unknown_cluster_label_shape_mismatch | 5 |
| monthly_match_label_surface_mismatch | 4 |
| seizure_free_to_no_reference_monthly_match | 3 |
| unknown_as_quantified_rate | 3 |
| unknown_vs_seizure_free | 2 |
| unknown_as_high_rate | 2 |
| cluster_collapsed_to_rate | 2 |
| frequent_overcalled | 1 |
| cluster_label_shape_mismatch | 1 |
| unknown_vs_no_reference | 1 |

### Invalid / abstained / missing

| Failure class | Count |
| --- | ---: |

### Taxonomy grouped by which metric failed

#### Misses against **normalized_exact**

| Failure class | Count |
| --- | ---: |
| other_semantic_mismatch | 17 |
| pragmatic_match_monthly_divergence | 16 |
| seizure_free_label_shape_mismatch | 15 |
| frequent_undercalled | 7 |
| purist_bin_boundary_within_pragmatic | 7 |
| unknown_cluster_label_shape_mismatch | 5 |
| monthly_match_label_surface_mismatch | 4 |
| seizure_free_to_no_reference_monthly_match | 3 |
| unknown_as_quantified_rate | 3 |
| cluster_collapsed_to_rate | 2 |
| unknown_as_high_rate | 2 |
| unknown_vs_seizure_free | 2 |
| cluster_label_shape_mismatch | 1 |
| frequent_overcalled | 1 |
| unknown_vs_no_reference | 1 |

#### Misses against **monthly**

| Failure class | Count |
| --- | ---: |
| other_semantic_mismatch | 17 |
| pragmatic_match_monthly_divergence | 16 |
| frequent_undercalled | 7 |
| purist_bin_boundary_within_pragmatic | 7 |
| unknown_as_quantified_rate | 3 |
| cluster_collapsed_to_rate | 2 |
| unknown_as_high_rate | 2 |
| unknown_vs_seizure_free | 2 |
| frequent_overcalled | 1 |
| unknown_vs_no_reference | 1 |

#### Misses against **purist**

| Failure class | Count |
| --- | ---: |
| other_semantic_mismatch | 17 |
| frequent_undercalled | 7 |
| purist_bin_boundary_within_pragmatic | 7 |
| unknown_as_quantified_rate | 3 |
| cluster_collapsed_to_rate | 2 |
| unknown_as_high_rate | 2 |
| unknown_vs_seizure_free | 2 |
| frequent_overcalled | 1 |
| unknown_vs_no_reference | 1 |

#### Misses against **pragmatic**

| Failure class | Count |
| --- | ---: |
| other_semantic_mismatch | 17 |
| frequent_undercalled | 7 |
| unknown_as_quantified_rate | 3 |
| unknown_as_high_rate | 2 |
| unknown_vs_seizure_free | 2 |
| cluster_collapsed_to_rate | 1 |
| frequent_overcalled | 1 |
| unknown_vs_no_reference | 1 |

## Interpretation

The four metrics form a strict hierarchy on valid predictions: normalized exact ⊂ monthly ⊂ Purist ⊂ Pragmatic. They do **not** always improve together in the sense that fixing one layer can leave coarser layers unchanged, but finer success never appears without coarser success.

The leading benchmark-severe failure class on this run is `other_semantic_mismatch` (17 scored misses). These are the first prompt or verifier targets; lower-tier metric wins should not hide them.

Cluster-format errors account for 8 scored misses, split between incomplete cluster labels (invalid), cluster structure swaps, and cluster collapsed to simple rates.

There are 8 **pragmatic-only** successes: same coarse bucket (infrequent vs frequent vs unknown vs no information) but wrong monthly value and Purist bin. These are clinically misleading if only Pragmatic accuracy is reported.

Purist-without-monthly cases: 16; pragmatic-without-monthly: 24. These arise when different labels land in the same bin but convert to different seizures/month.

Outside scored metrics: 0 abstentions/null outputs and 0 schema-invalid labels (mostly incomplete cluster surfaces and unsupported per-hour rates). These are excluded from the 281-record denominator but are full failures operationally.

## Record index

Full per-record rows are in the companion `records.jsonl` in the run `analysis/` folder.

| record_id | status | norm | mo | pur | prag | failure_class | gold | predicted |
| --- | --- | :---: | :---: | :---: | :---: | --- | --- | --- |
| gan_14485 | scored | Y | Y | Y | Y | all_metrics_match | 2 per 3 month | 2 per 3 month |
| gan_6532 | scored | N | Y | Y | Y | unknown_cluster_label_shape_mismatch | unknown, multiple per cluster | unknown |
| gan_10434 | scored | Y | Y | Y | Y | all_metrics_match | multiple cluster per week, 2 to 3 per cluster | multiple cluster per week, 2 to 3 per cluster |
| gan_4956 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 7 month | seizure free for 7 month |
| gan_13123 | scored | Y | Y | Y | Y | all_metrics_match | 1 per year | 1 per year |
| gan_4702 | scored | Y | Y | Y | Y | all_metrics_match | multiple per day | multiple per day |
| gan_10052 | scored | Y | Y | Y | Y | all_metrics_match | 4 cluster per 3 month, multiple per cluster | 4 cluster per 3 month, multiple per cluster |
| gan_2609 | scored | Y | Y | Y | Y | all_metrics_match | 1 per day | 1 per day |
| gan_1794 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 8 per 2 month | 6 per 2 month |
| gan_10618 | scored | N | Y | Y | Y | unknown_cluster_label_shape_mismatch | unknown, 4 to 6 per cluster | unknown |
| gan_15306 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 3 per 15 month | 2 to 3 per 15 month |
| gan_7894 | scored | N | Y | Y | Y | seizure_free_to_no_reference_monthly_match | seizure free for multiple year | no seizure frequency reference |
| gan_3246 | scored | Y | Y | Y | Y | all_metrics_match | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster |
| gan_4113 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 1 per 1 to 2 day | multiple per 2 day |
| gan_14881 | scored | Y | Y | Y | Y | all_metrics_match | 1 per month | 1 per month |
| gan_536 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 2 day | 1 per 2 day |
| gan_4709 | scored | N | N | N | N | other_semantic_mismatch | multiple per day | unknown |
| gan_9566 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_12679 | scored | Y | Y | Y | Y | all_metrics_match | 1 per day | 1 per day |
| gan_1584 | scored | Y | Y | Y | Y | all_metrics_match | 11 per month | 11 per month |
| gan_15997 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 10 per 3 month | 6 per 3 month |
| gan_17287 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 1 per 1 to 2 day | 1 per 2 day |
| gan_16251 | scored | Y | Y | Y | Y | all_metrics_match | 14 per 4 month | 14 per 4 month |
| gan_16772 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 9 per 5 month | 7 per month |
| gan_16825 | scored | Y | Y | Y | Y | all_metrics_match | 10 per 6 month | 10 per 6 month |
| gan_12950 | scored | Y | Y | Y | Y | all_metrics_match | 7 per 3 month | 7 per 3 month |
| gan_10047 | scored | Y | Y | Y | Y | all_metrics_match | 2 cluster per 3 month, multiple per cluster | 2 cluster per 3 month, multiple per cluster |
| gan_12810 | scored | Y | Y | Y | Y | all_metrics_match | 5 per 2 month | 5 per 2 month |
| gan_10398 | scored | Y | Y | Y | Y | all_metrics_match | 1 cluster per week, 2 per cluster | 1 cluster per week, 2 per cluster |
| gan_16041 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 9 per 3 month | 2 per month |
| gan_714 | scored | Y | Y | Y | Y | all_metrics_match | 2 per day | 2 per day |
| gan_12465 | scored | N | N | N | N | other_semantic_mismatch | 1 per day | unknown |
| gan_4011 | scored | Y | Y | Y | Y | all_metrics_match | 1 per month | 1 per month |
| gan_804 | scored | Y | Y | Y | Y | all_metrics_match | 1 per month | 1 per month |
| gan_22 | scored | Y | Y | Y | Y | all_metrics_match | 3 per day | 3 per day |
| gan_16335 | scored | Y | Y | Y | Y | all_metrics_match | 7 per 3 month | 7 per 3 month |
| gan_3867 | scored | Y | Y | Y | Y | all_metrics_match | 3 per day | 3 per day |
| gan_15923 | scored | Y | Y | Y | Y | all_metrics_match | 8 per 2 month | 8 per 2 month |
| gan_467 | scored | Y | Y | Y | Y | all_metrics_match | 9 per month | 9 per month |
| gan_2513 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 3 per 2 week | 2 to 3 per 2 week |
| gan_10993 | scored | Y | Y | Y | Y | all_metrics_match | 2 cluster per month, 2 to 4 per cluster | 2 cluster per month, 2 to 4 per cluster |
| gan_14792 | scored | Y | Y | Y | Y | all_metrics_match | 1 per month | 1 per month |
| gan_13574 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for multiple year | seizure free for multiple year |
| gan_5974 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_6607 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_12438 | scored | Y | Y | Y | Y | all_metrics_match | 1 per day | 1 per day |
| gan_4597 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 3 week | 1 per 3 week |
| gan_8564 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 6 month | seizure free for 6 month |
| gan_12130 | scored | Y | Y | Y | Y | all_metrics_match | multiple per week | multiple per week |
| gan_731 | scored | Y | Y | Y | Y | all_metrics_match | 1 per day | 1 per day |
| gan_1914 | scored | N | N | N | N | frequent_undercalled | 7 per 3 month | 2 per 3 month |
| gan_15639 | scored | Y | Y | Y | Y | all_metrics_match | 2 per week | 2 per week |
| gan_10583 | scored | N | Y | Y | Y | unknown_cluster_label_shape_mismatch | unknown, 2 to 3 per cluster | unknown |
| gan_14821 | scored | Y | Y | Y | Y | all_metrics_match | 1 per month | 1 per month |
| gan_6387 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_10984 | scored | Y | Y | Y | Y | all_metrics_match | 3 cluster per month, 3 to 4 per cluster | 3 cluster per month, 3 to 4 per cluster |
| gan_8264 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 4 month | seizure free for 4 month |
| gan_14250 | scored | Y | Y | Y | Y | all_metrics_match | 2 per month | 2 per month |
| gan_15876 | scored | Y | Y | Y | Y | all_metrics_match | 6 per week | 6 per week |
| gan_1463 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 3 per month | 2 per month |
| gan_14689 | scored | Y | Y | Y | Y | all_metrics_match | 3 per 2 month | 3 per 2 month |
| gan_4100 | scored | N | N | N | N | other_semantic_mismatch | 1 per 2 to 3 week | unknown |
| gan_15771 | scored | N | N | N | N | other_semantic_mismatch | 3 per week | unknown |
| gan_9365 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 2 day | 1 per 2 day |
| gan_198 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 4 week | 1 per 4 week |
| gan_10003 | scored | Y | Y | Y | Y | all_metrics_match | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster |
| gan_16991 | scored | Y | Y | Y | Y | all_metrics_match | multiple per month | multiple per month |
| gan_3623 | scored | N | N | N | N | other_semantic_mismatch | 7 per week | unknown |
| gan_3692 | scored | Y | Y | Y | Y | all_metrics_match | 9 per week | 9 per week |
| gan_17 | scored | Y | Y | Y | Y | all_metrics_match | 2 per day | 2 per day |
| gan_10553 | scored | N | Y | Y | Y | unknown_cluster_label_shape_mismatch | unknown, 2 to 3 per cluster | unknown |
| gan_14002 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_2725 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 2 week | 1 per 2 week |
| gan_2226 | scored | Y | Y | Y | Y | all_metrics_match | 3 to 10 per 2 week | 3 to 10 per 2 week |
| gan_11380 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_14214 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 4 per month | 2 to 4 per month |
| gan_3630 | scored | N | N | N | N | other_semantic_mismatch | 7 per week | unknown |
| gan_16753 | scored | Y | Y | Y | Y | all_metrics_match | 19 per 6 month | 19 per 6 month |
| gan_12667 | scored | Y | Y | Y | Y | all_metrics_match | 1 per day | 1 per day |
| gan_15442 | scored | Y | Y | Y | Y | all_metrics_match | 1 cluster per 4 day, 2 per cluster | 1 cluster per 4 day, 2 per cluster |
| gan_2262 | scored | Y | Y | Y | Y | all_metrics_match | 7 to 9 per 3 week | 7 to 9 per 3 week |
| gan_11408 | scored | Y | Y | Y | Y | all_metrics_match | no seizure frequency reference | no seizure frequency reference |
| gan_12218 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 1 per day | multiple per day |
| gan_10862 | scored | Y | Y | Y | Y | all_metrics_match | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster |
| gan_11841 | scored | Y | Y | Y | Y | all_metrics_match | no seizure frequency reference | no seizure frequency reference |
| gan_14628 | scored | Y | Y | Y | Y | all_metrics_match | 2 per 2 month | 2 per 2 month |
| gan_10996 | scored | Y | Y | Y | Y | all_metrics_match | 1 to 2 cluster per month, 4 per cluster | 1 to 2 cluster per month, 4 per cluster |
| gan_16938 | scored | N | N | N | N | frequent_undercalled | 2 per week | 2 per 2 month |
| gan_14081 | scored | N | N | N | N | unknown_as_quantified_rate | unknown | 1 to 3 per 3 month |
| gan_6131 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_10509 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_14354 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 4 per 3 month | 2 to 4 per 3 month |
| gan_3512 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_11216 | scored | N | N | N | N | unknown_vs_seizure_free | unknown | seizure free for 4 month |
| gan_9424 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 10 per 9 month | 2 per month |
| gan_3225 | scored | Y | Y | Y | Y | all_metrics_match | 1 cluster per month, 3 to 10 per cluster | 1 cluster per month, 3 to 10 per cluster |
| gan_5976 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_7818 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 2 year | seizure free for 2 year |
| gan_13598 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for multiple year | seizure free for multiple year |
| gan_14137 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_14973 | scored | Y | Y | Y | Y | all_metrics_match | 1 per month | 1 per month |
| gan_11044 | scored | Y | Y | Y | Y | all_metrics_match | 1 cluster per 3 month, 2 to 4 per cluster | 1 cluster per 3 month, 2 to 4 per cluster |
| gan_14040 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_1883 | scored | N | N | N | N | frequent_undercalled | 4 per 3 month | 3 per 3 month |
| gan_1640 | scored | Y | Y | Y | Y | all_metrics_match | 5 per week | 5 per week |
| gan_12314 | scored | Y | Y | Y | Y | all_metrics_match | 3 per week | 3 per week |
| gan_3325 | scored | Y | Y | Y | Y | all_metrics_match | 3 per week | 3 per week |
| gan_16780 | scored | N | N | N | N | other_semantic_mismatch | 3 per 7 month | unknown |
| gan_14146 | scored | N | N | N | N | unknown_as_high_rate | unknown | 3 per 2 month |
| gan_12296 | scored | Y | Y | Y | Y | all_metrics_match | 3 to 4 per day | 3 to 4 per day |
| gan_2549 | scored | Y | Y | Y | Y | all_metrics_match | 7 to 8 per 2 month | 7 to 8 per 2 month |
| gan_128 | scored | Y | Y | Y | Y | all_metrics_match | 17 per month | 17 per month |
| gan_13595 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for multiple year | seizure free for multiple year |
| gan_12145 | scored | Y | Y | Y | Y | all_metrics_match | multiple per week | multiple per week |
| gan_3300 | scored | Y | Y | Y | Y | all_metrics_match | 9 per month | 9 per month |
| gan_6094 | scored | N | N | N | N | other_semantic_mismatch | 3 per month | unknown |
| gan_2824 | scored | Y | Y | Y | Y | all_metrics_match | 1 per day | 1 per day |
| gan_7872 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for multiple month | seizure free for multiple month |
| gan_1486 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 3 per month | 2 per month |
| gan_7431 | scored | N | Y | Y | Y | monthly_match_label_surface_mismatch | 1 per month | 2 per 2 month |
| gan_11874 | scored | Y | Y | Y | Y | all_metrics_match | no seizure frequency reference | no seizure frequency reference |
| gan_3095 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 12 month | seizure free for 12 month |
| gan_15847 | scored | Y | Y | Y | Y | all_metrics_match | 6 per week | 6 per week |
| gan_3864 | scored | N | Y | Y | Y | monthly_match_label_surface_mismatch | 3 per day | multiple per day |
| gan_5551 | scored | Y | Y | Y | Y | all_metrics_match | multiple per day | multiple per day |
| gan_8160 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for multiple month | seizure free for multiple month |
| gan_2740 | scored | Y | Y | Y | Y | all_metrics_match | 1 per month | 1 per month |
| gan_10292 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_12823 | scored | Y | Y | Y | Y | all_metrics_match | 9 per month | 9 per month |
| gan_338 | scored | Y | Y | Y | Y | all_metrics_match | multiple per month | multiple per month |
| gan_12562 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 1 per day | 3 to 4 per week |
| gan_10031 | scored | Y | Y | Y | Y | all_metrics_match | 1 cluster per week, multiple per cluster | 1 cluster per week, multiple per cluster |
| gan_15737 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 3 per week | 2 to 3 per week |
| gan_16883 | scored | N | N | N | N | other_semantic_mismatch | 4 per 3 month | unknown |
| gan_10447 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_15783 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 3 per week | 2 to 3 per week |
| gan_234 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 2 month | 1 per 2 month |
| gan_531 | scored | Y | Y | Y | Y | all_metrics_match | 12 to 30 per 3 month | 12 to 30 per 3 month |
| gan_4996 | scored | N | Y | Y | Y | seizure_free_label_shape_mismatch | seizure free for 16 month | seizure free for multiple month |
| gan_3261 | scored | Y | Y | Y | Y | all_metrics_match | 2 cluster per month, 4 per cluster | 2 cluster per month, 4 per cluster |
| gan_15513 | scored | N | N | N | Y | cluster_collapsed_to_rate | 1 cluster per 4 to 5 day, 2 to 3 per cluster | 2 to 3 per day |
| gan_16408 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 3 day | 1 per 3 day |
| gan_2652 | scored | Y | Y | Y | Y | all_metrics_match | 1 per day | 1 per day |
| gan_6077 | scored | N | N | N | N | unknown_as_quantified_rate | unknown | 1 per 8 month |
| gan_14655 | scored | Y | Y | Y | Y | all_metrics_match | 2 per 2 month | 2 per 2 month |
| gan_15404 | scored | Y | Y | Y | Y | all_metrics_match | 1 cluster per 4 month, 3 to 4 per cluster | 1 cluster per 4 month, 3 to 4 per cluster |
| gan_12871 | scored | N | N | N | N | frequent_undercalled | 5 per 2 month | 5 per year |
| gan_7882 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 6 month | seizure free for 6 month |
| gan_13450 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 1 year | seizure free for 1 year |
| gan_31 | scored | Y | Y | Y | Y | all_metrics_match | 4 per day | 4 per day |
| gan_3113 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 14 month | seizure free for 14 month |
| gan_5197 | scored | N | Y | Y | Y | seizure_free_label_shape_mismatch | seizure free for multiple month | seizure free for 6 month |
| gan_12319 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 3 per week | 2 to 3 per week |
| gan_6624 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_4602 | scored | N | N | N | N | other_semantic_mismatch | 1 per 7 to 10 day | unknown |
| gan_5977 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_11706 | scored | Y | Y | Y | Y | all_metrics_match | no seizure frequency reference | no seizure frequency reference |
| gan_243 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 4 month | 1 per 4 month |
| gan_4831 | scored | N | Y | Y | Y | seizure_free_label_shape_mismatch | seizure free for multiple month | seizure free for 6 month |
| gan_9179 | scored | N | Y | Y | Y | seizure_free_label_shape_mismatch | seizure free for multiple month | seizure free for 1 month |
| gan_1070 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 3 to 4 per week | 4 per week |
| gan_17279 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 1 per 4 to 5 week | 1 per 4 week |
| gan_13487 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for multiple year | seizure free for multiple year |
| gan_8858 | scored | N | Y | Y | Y | seizure_free_label_shape_mismatch | seizure free for multiple month | seizure free for 1 year |
| gan_8113 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 14 month | seizure free for 14 month |
| gan_14965 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 3 month | 1 per 3 month |
| gan_3747 | scored | Y | Y | Y | Y | all_metrics_match | 3 per day | 3 per day |
| gan_3329 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 3 per day | 2 to 3 per day |
| gan_2486 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 3 per 3 month | 2 to 3 per 3 month |
| gan_12362 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 3 per day | 2 to 3 per day |
| gan_3355 | scored | N | Y | Y | Y | monthly_match_label_surface_mismatch | 1 per 3 month | 2 per 6 month |
| gan_11434 | scored | Y | Y | Y | Y | all_metrics_match | no seizure frequency reference | no seizure frequency reference |
| gan_13416 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for multiple year | seizure free for multiple year |
| gan_11196 | scored | Y | Y | Y | Y | all_metrics_match | 3 cluster per month, 5 per cluster | 3 cluster per month, 5 per cluster |
| gan_9279 | scored | Y | Y | Y | Y | all_metrics_match | 1 to 2 per week | 1 to 2 per week |
| gan_4700 | scored | Y | Y | Y | Y | all_metrics_match | multiple per day | multiple per day |
| gan_13993 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_5379 | scored | N | Y | Y | Y | seizure_free_label_shape_mismatch | seizure free for multiple month | seizure free for 6 month |
| gan_15129 | scored | Y | Y | Y | Y | all_metrics_match | 4 per 15 month | 4 per 15 month |
| gan_12246 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 1 to 2 per day | multiple per day |
| gan_7573 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 2 week | 1 per 2 week |
| gan_1357 | scored | Y | Y | Y | Y | all_metrics_match | 1 per day | 1 per day |
| gan_7316 | scored | Y | Y | Y | Y | all_metrics_match | 1 to 2 per month | 1 to 2 per month |
| gan_2795 | scored | Y | Y | Y | Y | all_metrics_match | 1 per week | 1 per week |
| gan_9063 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 8 month | seizure free for 8 month |
| gan_9943 | scored | N | N | N | N | cluster_collapsed_to_rate | 1 cluster per 4 to 5 week, multiple per cluster | unknown |
| gan_16750 | scored | Y | Y | Y | Y | all_metrics_match | 6 per 7 month | 6 per 7 month |
| gan_15127 | scored | Y | Y | Y | Y | all_metrics_match | 5 per 13 month | 5 per 13 month |
| gan_6661 | scored | N | Y | Y | Y | monthly_match_label_surface_mismatch | 0.5 per week | 3 per 6 week |
| gan_5351 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 18 month | seizure free for 18 month |
| gan_3791 | scored | Y | Y | Y | Y | all_metrics_match | 10 per year | 10 per year |
| gan_16523 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 5 day | 1 per 5 day |
| gan_7884 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for multiple month | seizure free for multiple month |
| gan_14748 | scored | Y | Y | Y | Y | all_metrics_match | 2 per 3 month | 2 per 3 month |
| gan_10410 | scored | Y | Y | Y | Y | all_metrics_match | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster |
| gan_3452 | scored | Y | Y | Y | Y | all_metrics_match | 6 to 8 per month | 6 to 8 per month |
| gan_2781 | scored | Y | Y | Y | Y | all_metrics_match | 1 per week | 1 per week |
| gan_5682 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 4 per month | 2 to 4 per month |
| gan_4919 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 2 year | seizure free for 2 year |
| gan_8577 | scored | N | Y | Y | Y | seizure_free_label_shape_mismatch | seizure free for multiple month | seizure free for 18 month |
| gan_2135 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_14025 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_9483 | scored | Y | Y | Y | Y | all_metrics_match | 8 per 6 month | 8 per 6 month |
| gan_3340 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 3 per month | 2 to 3 per month |
| gan_15255 | scored | Y | Y | Y | Y | all_metrics_match | multiple cluster per 15 month, multiple per cluster | multiple cluster per 15 month, multiple per cluster |
| gan_8852 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 8 month | seizure free for 8 month |
| gan_7783 | scored | N | Y | Y | Y | seizure_free_label_shape_mismatch | seizure free for multiple month | seizure free for 3 month |
| gan_11207 | scored | Y | Y | Y | Y | all_metrics_match | 2 cluster per month, 6 per cluster | 2 cluster per month, 6 per cluster |
| gan_115 | scored | Y | Y | Y | Y | all_metrics_match | 7 to 8 per month | 7 to 8 per month |
| gan_10673 | scored | Y | Y | Y | Y | all_metrics_match | 1 cluster per month, multiple per cluster | 1 cluster per month, multiple per cluster |
| gan_13058 | scored | Y | Y | Y | Y | all_metrics_match | 2 per 7 month | 2 per 7 month |
| gan_2369 | scored | N | N | N | N | other_semantic_mismatch | 3 to 4 per month | unknown |
| gan_8224 | scored | N | Y | Y | Y | seizure_free_label_shape_mismatch | seizure free for multiple month | seizure free for 3 month |
| gan_15982 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 9 per 2 month | 8 per month |
| gan_11259 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_744 | scored | N | N | N | N | frequent_undercalled | multiple per week | 1 per 2 month |
| gan_4591 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 5 month | 1 per 5 month |
| gan_14271 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 3 per month | 2 to 3 per month |
| gan_13290 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 4 per 6 month | 2 per 6 month |
| gan_6509 | scored | N | N | N | N | other_semantic_mismatch | 1 per week | unknown |
| gan_8116 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 12 month | seizure free for 12 month |
| gan_16645 | scored | Y | Y | Y | Y | all_metrics_match | 5 per 7 month | 5 per 7 month |
| gan_3102 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 14 month | seizure free for 14 month |
| gan_9002 | scored | N | N | N | N | other_semantic_mismatch | 7 per year | seizure free for multiple month |
| gan_8474 | scored | N | Y | Y | Y | seizure_free_label_shape_mismatch | seizure free for multiple month | seizure free for 6 month |
| gan_3291 | scored | Y | Y | Y | Y | all_metrics_match | 9 per month | 9 per month |
| gan_15193 | scored | N | N | N | N | frequent_overcalled | multiple per 13 month | multiple per month |
| gan_16574 | scored | N | N | N | N | other_semantic_mismatch | 1 per 4 day | unknown |
| gan_4378 | scored | N | N | N | N | frequent_undercalled | 3 per 2 month | 3 per year |
| gan_6029 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_180 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 1 per 7 day | 1 per week |
| gan_6684 | scored | Y | Y | Y | Y | all_metrics_match | 3 per 4 month | 3 per 4 month |
| gan_14390 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 2 per 3 month | 1 per 4 month |
| gan_10751 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_12348 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 3 per week | 2 to 3 per week |
| gan_6296 | scored | Y | Y | Y | Y | all_metrics_match | 3 per 4 month | 3 per 4 month |
| gan_5092 | scored | N | Y | Y | Y | seizure_free_to_no_reference_monthly_match | seizure free for multiple month | no seizure frequency reference |
| gan_10884 | scored | Y | Y | Y | Y | all_metrics_match | 1 cluster per week, 3 to 4 per cluster | 1 cluster per week, 3 to 4 per cluster |
| gan_848 | scored | Y | Y | Y | Y | all_metrics_match | 1 per year | 1 per year |
| gan_16947 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 2 per week | 4 per 2 month |
| gan_11411 | scored | Y | Y | Y | Y | all_metrics_match | no seizure frequency reference | no seizure frequency reference |
| gan_11221 | scored | N | N | N | N | unknown_vs_seizure_free | unknown | seizure free for 4 month |
| gan_6153 | scored | N | N | N | N | other_semantic_mismatch | 9 per month | unknown |
| gan_12877 | scored | Y | Y | Y | Y | all_metrics_match | 10 per 4 month | 10 per 4 month |
| gan_8203 | scored | N | Y | Y | Y | seizure_free_label_shape_mismatch | seizure free for multiple month | seizure free for 6 month |
| gan_1497 | scored | Y | Y | Y | Y | all_metrics_match | 3 per month | 3 per month |
| gan_17239 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 4 per week | 1 per week |
| gan_182 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 2 day | 1 per 2 day |
| gan_14036 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_7290 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_13019 | scored | N | N | N | N | frequent_undercalled | 9 per 3 month | 1 per 3 month |
| gan_13376 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 2 year | seizure free for 2 year |
| gan_17006 | scored | Y | Y | Y | Y | all_metrics_match | 2 per week | 2 per week |
| gan_5866 | scored | Y | Y | Y | Y | all_metrics_match | 4 per 6 week | 4 per 6 week |
| gan_10074 | scored | Y | Y | Y | Y | all_metrics_match | 5 cluster per month, multiple per cluster | 5 cluster per month, multiple per cluster |
| gan_750 | scored | Y | Y | Y | Y | all_metrics_match | multiple per week | multiple per week |
| gan_14076 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_8844 | scored | N | Y | Y | Y | seizure_free_to_no_reference_monthly_match | seizure free for 15 month | no seizure frequency reference |
| gan_15168 | scored | N | N | N | N | other_semantic_mismatch | multiple per 15 month | unknown |
| gan_3015 | scored | N | Y | Y | Y | seizure_free_label_shape_mismatch | seizure free for 12 month | seizure free for 1 year |
| gan_5653 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 2 day | 1 per 2 day |
| gan_10542 | scored | N | Y | Y | Y | unknown_cluster_label_shape_mismatch | unknown, 2 to 4 per cluster | unknown |
| gan_6987 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_8723 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for multiple month | seizure free for multiple month |
| gan_16529 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 5 day | 1 per 5 day |
| gan_6763 | scored | Y | Y | Y | Y | all_metrics_match | 1 per week | 1 per week |
| gan_14092 | scored | N | N | N | N | unknown_as_high_rate | unknown | 5 per 2 month |
| gan_15302 | scored | Y | Y | Y | Y | all_metrics_match | 1 to 2 per 14 month | 1 to 2 per 14 month |
| gan_5837 | scored | Y | Y | Y | Y | all_metrics_match | 2 cluster per 3 week, multiple per cluster | 2 cluster per 3 week, multiple per cluster |
| gan_1694 | scored | N | Y | Y | Y | cluster_label_shape_mismatch | 1 cluster per 2 week, 3 per cluster | 3 per 2 week |
| gan_5954 | scored | Y | Y | Y | Y | all_metrics_match | 2 per week | 2 per week |
| gan_16422 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 1 per 2 to 3 day | 1 to 2 per 3 day |
| gan_7341 | scored | Y | Y | Y | Y | all_metrics_match | unknown | unknown |
| gan_16964 | scored | N | N | N | Y | purist_bin_boundary_within_pragmatic | 2 per week | 5 per 2 month |
| gan_2456 | scored | Y | Y | Y | Y | all_metrics_match | 6 to 7 per 2 week | 6 to 7 per 2 week |
| gan_7420 | scored | N | N | N | N | other_semantic_mismatch | 1 to 2 per 2 week | unknown |
| gan_2354 | scored | Y | Y | Y | Y | all_metrics_match | 6 to 7 per week | 6 to 7 per week |
| gan_11399 | scored | N | N | N | N | unknown_as_quantified_rate | unknown | 1 per month |
| gan_11733 | scored | Y | Y | Y | Y | all_metrics_match | no seizure frequency reference | no seizure frequency reference |
| gan_13149 | scored | Y | Y | Y | Y | all_metrics_match | 3 per year | 3 per year |
| gan_9109 | scored | N | N | N | N | unknown_vs_no_reference | unknown | no seizure frequency reference |
| gan_3118 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for multiple month | seizure free for multiple month |
| gan_11763 | scored | Y | Y | Y | Y | all_metrics_match | no seizure frequency reference | no seizure frequency reference |
| gan_11748 | scored | Y | Y | Y | Y | all_metrics_match | no seizure frequency reference | no seizure frequency reference |
| gan_2487 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 3 per 3 month | 2 to 3 per 3 month |
| gan_11804 | scored | Y | Y | Y | Y | all_metrics_match | no seizure frequency reference | no seizure frequency reference |
| gan_4992 | scored | Y | Y | Y | Y | all_metrics_match | seizure free for 11 month | seizure free for 11 month |
| gan_2366 | scored | Y | Y | Y | Y | all_metrics_match | 2 to 4 per year | 2 to 4 per year |
| gan_5082 | scored | N | Y | Y | Y | seizure_free_label_shape_mismatch | seizure free for multiple month | seizure free for 6 month |
| gan_9526 | scored | Y | Y | Y | Y | all_metrics_match | 4 per 8 month | 4 per 8 month |
| gan_8893 | scored | N | Y | Y | Y | seizure_free_label_shape_mismatch | seizure free for multiple month | seizure free for 4 month |
| gan_8645 | scored | N | Y | Y | Y | seizure_free_label_shape_mismatch | seizure free for multiple month | seizure free for 6 month |
| gan_11035 | scored | Y | Y | Y | Y | all_metrics_match | 1 cluster per 3 month, 1 per cluster | 1 cluster per 3 month, 1 per cluster |
| gan_8002 | scored | N | N | Y | Y | pragmatic_match_monthly_divergence | 1 per 6 to 8 week | 1 per 2 month |
| gan_13190 | scored | Y | Y | Y | Y | all_metrics_match | 1 per 5 month | 1 per 5 month |
| gan_15240 | scored | Y | Y | Y | Y | all_metrics_match | multiple cluster per 12 month, multiple per cluster | multiple cluster per 12 month, multiple per cluster |
| gan_14562 | scored | Y | Y | Y | Y | all_metrics_match | 3 per 6 month | 3 per 6 month |
| gan_6836 | scored | Y | Y | Y | Y | all_metrics_match | 1 per week | 1 per week |
| gan_11734 | scored | Y | Y | Y | Y | all_metrics_match | no seizure frequency reference | no seizure frequency reference |
