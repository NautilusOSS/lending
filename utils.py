from algopy import (
    Account,
    Asset,
    Global,
    Txn,
    UInt64,
    gtxn,
    itxn,
    op,
    subroutine,
)

##############################################
# function: require_payment (internal)
# arguments: None
# purpose: check payment
# pre-conditions: None
# post-conditions: None
##############################################
@subroutine
def require_payment(who: Account, rel_group_index: UInt64) -> UInt64:
    ref_group_index = Txn.group_index
    assert ref_group_index > 0, "group index greater than zero"
    payment_group_index = ref_group_index - rel_group_index
    assert gtxn.PaymentTransaction(payment_group_index).sender == who, "payment sender accurate"
    assert gtxn.PaymentTransaction(payment_group_index).receiver == Global.current_application_address, "payment receiver accurate"
    return gtxn.PaymentTransaction(payment_group_index).amount

##############################################
# function: require_payment (internal)
# arguments: None
# purpose: check payment
# pre-conditions: None
# post-conditions: None
##############################################
@subroutine
def require_asset_transfer(who: Account, rel_group_index: UInt64, asset: Asset) -> UInt64:
    ref_group_index = Txn.group_index
    assert ref_group_index > 0, "group index greater than zero"
    payment_group_index = ref_group_index - rel_group_index
    assert gtxn.AssetTransferTransaction(payment_group_index).sender == who, "axfer sender accurate"
    assert gtxn.AssetTransferTransaction(payment_group_index).asset_receiver == Global.current_application_address, "axfer receiver accurate"
    assert gtxn.AssetTransferTransaction(payment_group_index).xfer_asset == asset, "axfer asset accurate"
    return gtxn.AssetTransferTransaction(payment_group_index).asset_amount

##############################################
# function: get_available_balance (internal)
# purpose: get available balance
# returns: app balance available for spending
##############################################
@subroutine
def get_available_balance() -> UInt64:
    balance = op.balance(Global.current_application_address)
    min_balance = op.Global.min_balance
    available_balance = balance - min_balance
    return available_balance

##############################################
# function: app_asset_opt_in (internal)
# arguments: asset
# purpose: opt-in to asset
# post-conditions: asset opt-in
##############################################
@subroutine
def app_asset_opt_in(asset: Asset) -> None:
    itxn.AssetTransfer(
        asset_receiver=Global.current_application_address,
        xfer_asset=asset,
    ).submit()