import json
import pandas as pd
import plotly.express as px

export = "./last_week_raven.json"
data = json.loads(open(export, "r").read())

# normalize
df = pd.DataFrame(data)
df["failed"] = df["transactionHash"].isnull()
df['score_norm'] = df['score'].combine_first(
    df['scoreDiscounted']).combine_first(df["scoreProtocol"])
df["score_norm"] = df["score_norm"].astype("float64") / 1e18
df['order_num'] = df["orders"].map(len)
df["obj_value"] = df["objective"].apply(pd.Series)["total"] / 1e18


def protocol_overbid(solver, _df):
    proc = _df.copy()
    # rank solutions by obj_value
    proc["rank"] = df.groupby(["competitionSimulationBlock"])[
        "obj_value"].rank(ascending=False)
    proc["overbid"] = proc["score_norm"] > proc["obj_value"]
    proc = proc[proc["failed"] == False]
    loss_auctions_best_val = proc[proc["rank"] == 1.0]
    loss_auctions_best_val = loss_auctions_best_val[loss_auctions_best_val["ranking"] != 1]
    loss_auctions_best_val = loss_auctions_best_val[loss_auctions_best_val["failed"] == False]
    # did not discount
    loss_auctions_best_val = loss_auctions_best_val[loss_auctions_best_val["score_norm"] >= loss_auctions_best_val["obj_value"]]
    loss_auctions_best_val.set_index(
        "competitionSimulationBlock", inplace=True)
    print(loss_auctions_best_val)

    overbidder = proc[proc["ranking"] == 1]
    overbidder = overbidder[overbidder["overbid"]]
    overbidder.set_index("competitionSimulationBlock", inplace=True)
    mask = loss_auctions_best_val.index.isin(overbidder.index)
    loss_auctions_best_val = loss_auctions_best_val[mask]
    overbidder = overbidder.loc[loss_auctions_best_val.index]
    # loss_auctions = loss_auctions.loc[loss_auctions_rank2.index]

    overbidder["obj_loss"] = overbidder["obj_value"] - \
        loss_auctions_best_val["obj_value"]
    significant_idx = overbidder["obj_loss"] < -0.00005
    overbidder = overbidder[significant_idx]
    loss_auctions_best_val = loss_auctions_best_val[significant_idx]
    loss_auctions_best_val["solver_was_better_than_overbidder"] = loss_auctions_best_val["obj_value"] - \
        overbidder["obj_value"]
    loss_auctions_best_val["overbidder"] = overbidder["solver"]
    loss_auctions_best_val["best"] = loss_auctions_best_val["solver"]
    loss_auctions_best_val["size"] = 0.25
    print(overbidder)
    print(loss_auctions_best_val)
    print("TOTAL LOSS", overbidder["obj_loss"].sum())

    solver_loss = loss_auctions_best_val[loss_auctions_best_val["solver"] == solver].index
    solver_loss = overbidder.loc[solver_loss]["obj_value"] - loss_auctions_best_val.loc[solver_loss]["obj_value"]
    print("TOTAL SOLVER LOSS", solver_loss.sum())

    fig = px.scatter_3d(loss_auctions_best_val,  x='best',
                        y="overbidder", z="solver_was_better_than_overbidder", color="solver",  size="size")
    fig.show()

    # rank2 = proc[proc["rank"] == 2.0 and (proc["rank"] == 1 and proc["ranking"] != 1)]
    # loss_auctions_raven = loss_auctions[loss_auctions["solver"] == "Raven"]
    # print(loss_auctions_raven)


# 4/ Surplus loss where obj value was smaller than overbid value
protocol_overbid("Raven", df)

