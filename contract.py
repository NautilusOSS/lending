from algopy import (
    ARC4Contract,
    Account,
    Asset,
    Global,
    OnCompleteAction,
    Txn,
    UInt64,
    arc4,
    itxn,
    op,
)
from utils import require_payment, require_asset_transfer, app_asset_opt_in


class AssetLendingBase(ARC4Contract):
    ##############################################
    # function: __init__ (builtin)
    # arguments: None
    # purpose: construct initial state
    # pre-conditions: None
    # post-conditions: initial state set
    ##############################################
    def __init__(self) -> None:
        self.lender = Global.creator_address
        self.borrower = Account()  # zero address
        self.lend_type = UInt64()  # 0
        self.lend_payment_asset_id = UInt64()  # 0
        self.lend_asset_id = UInt64()  # 0
        self.lend_amount = UInt64()  # 0
        self.lend_paid = UInt64()  # 0
        self.lend_status = UInt64()  # ""
        self.lend_payback = UInt64()  # 0
        self.lend_date = UInt64()  # 0
        self.lend_time = UInt64()  # 0

    ##############################################
    # function: setup
    # arguments:
    # - lend_type, the type of lending
    # - lend_payment_asset_id, the asset to be lent
    # - lend_asset_id, the asset to be paid back
    # purpose: setup lending
    # post-conditions: lend_status setup
    ##############################################
    @arc4.abimethod
    def setup(
        self,
        lend_type: UInt64,
        lend_payment_asset_id: UInt64,
        lend_asset_id: UInt64,
    ) -> None:
        pass

    ##############################################
    # function: fund
    # arguments:
    # - lend_payback, the amount to pay back
    # - lend_time, the time to pay back
    # purpose: fund the contract
    # post-conditions: lend_status funded
    ##############################################
    @arc4.abimethod
    def fund(
        self,
        lend_amount: arc4.UInt64,
        lend_payback: arc4.UInt64,
        lend_time: arc4.UInt64,
    ) -> None:
        pass

    ##############################################
    # function: lend_nft
    # arguments: None
    # purpose: lend the nft
    # post-conditions: lend_status lent
    ##############################################
    @arc4.abimethod
    def lend_nft(
        self,
    ) -> None:
        pass

    ##############################################
    # function: pay_debt
    # arguments: None
    # purpose: pay dept
    # post-conditions: lend_status paid
    ##############################################
    @arc4.abimethod
    def pay_debt(self) -> None:
        pass

    ##############################################
    # function: claim_nft
    # arguments: None
    # purpose: claim the nft
    # post-conditions: lend_status claimed
    ##############################################
    @arc4.abimethod
    def claim_nft(self) -> None:
        pass

    ##############################################
    # function: claim_debt
    # arguments: None
    # purpose: claim the debt
    # post-conditions: lend_status claimed
    ##############################################
    @arc4.abimethod
    def claim_debt(self) -> None:
        pass

    ##############################################
    # function: close
    # purpose: deletes contract
    # pre-conditions:
    # - mab is 0
    # post-conditions:
    # - contract is deleted
    # - account closed out to owner if it has a balance
    # notes:
    # - should be alled with onCompletion
    #   deleteApplication
    ##############################################
    @arc4.abimethod(allow_actions=[OnCompleteAction.DeleteApplication])
    def close(self) -> None:
        oca = Txn.on_completion
        if oca == OnCompleteAction.DeleteApplication:
            itxn.Payment(receiver=self.lender, close_remainder_to=self.lender).submit()
        else:
            op.err()

    ##############################################
    # function: opt_out
    # purpose: opt out asset from the contract
    ##############################################
    @arc4.abimethod
    def opt_out(self) -> None:
        ###########################################
        assert self.lend_status <= UInt64(2), "not lended"
        ###########################################
        lend_asset = Asset(self.lend_asset_id)
        itxn.AssetTransfer(
            asset_amount=UInt64(0),
            asset_receiver=lend_asset.creator,
            xfer_asset=lend_asset,
            asset_close_to=lend_asset.creator,
        ).submit()
        ###########################################
        self.lend_status = UInt64(5)
        self.lend_asset_id = UInt64(0)
        ###########################################


class NTAssetLending(AssetLendingBase):
    ##############################################
    # function: setup
    # purpose: prepare for lending
    # pre-conditions:
    # - lend_status is 0
    # post-conditions:
    # - lend_asset set
    # - lend_payback set
    # - lend_time set
    # - lender set
    # - lend_amount set
    # notes:
    # - should be called by app creator
    ##############################################
    @arc4.abimethod
    def setup(
        self,
        lend_type: UInt64,
        lend_payment_asset_id: UInt64,
        lend_asset_id: UInt64,
    ) -> None:
        ##########################################
        assert self.lend_status == UInt64(0), "lend_status not initialized"
        ##########################################
        lend_asset = Asset(lend_asset_id)
        assert lend_asset.clawback == Global.zero_address, "lend_asset not clawback"
        assert lend_asset.freeze == Global.zero_address, "lend_asset not freeze"
        ##########################################
        app_asset_opt_in(lend_asset)
        ##########################################
        self.lend_type = UInt64(1)
        self.lend_asset_id = lend_asset_id
        self.lend_status = UInt64(1)

    ##############################################
    # function: fund
    # arguments: None
    # purpose: fund the contract
    # post-conditions: lend_status funded
    ##############################################
    @arc4.abimethod
    def fund(
        self,
        lend_amount: arc4.UInt64,
        lend_payback: arc4.UInt64,
        lend_time: arc4.UInt64,
    ) -> None:
        ##########################################
        assert self.lend_status == UInt64(1), "lend_status not setup"
        ##########################################
        lender = Txn.sender
        payment_amount = require_payment(Txn.sender, UInt64(1))
        assert payment_amount == lend_amount, "payment amount accurate"
        assert payment_amount > UInt64(2000000), "payment amount accurate"
        assert lend_payback > payment_amount + UInt64(2000000), "lend_payback accurate"
        assert lend_time > UInt64(0), "lend_time accurate"
        ##########################################
        self.lender = lender
        self.lend_amount = payment_amount
        self.lend_payback = lend_payback.native
        self.lend_time = lend_time.native
        self.lend_status = UInt64(2)

    ##############################################
    # function: lend_nft
    # arguments: None
    # purpose: lend the nft
    # post-conditions: lend_status lent
    ##############################################
    @arc4.abimethod
    def lend_nft(
        self,
    ) -> None:
        ##########################################
        assert self.lend_status == UInt64(2), "lend_status not funded"
        ##########################################
        lend_asset = Asset(self.lend_asset_id)
        axfer_amount = require_asset_transfer(Txn.sender, UInt64(1), lend_asset)
        assert axfer_amount == UInt64(1), "axfer amount accurate"
        ##########################################
        borrower = Txn.sender
        ##########################################
        itxn.Payment(amount=self.lend_amount, receiver=borrower).submit()
        ##########################################
        self.borrower = borrower
        self.lend_date = Global.latest_timestamp
        self.lend_status = UInt64(3)

    ##############################################
    # function: pay_debt
    # arguments: None
    # purpose: pay dept
    # post-conditions: lend_status paid
    ##############################################
    @arc4.abimethod
    def pay_debt(self) -> None:
        ##########################################
        assert self.lend_status == UInt64(3), "lend_status not lent"
        ##########################################
        assert Txn.sender == self.borrower, "sender accurate"
        payment_amount = require_payment(Txn.sender, UInt64(1))
        assert payment_amount == self.lend_payback, "payment amount accurate"
        ##########################################
        lend_asset = Asset(self.lend_asset_id)
        itxn.AssetTransfer(
            asset_amount=UInt64(1),
            asset_receiver=self.borrower,
            xfer_asset=lend_asset,
            asset_close_to=lend_asset.creator,
        ).submit()
        ##########################################
        self.lend_paid = payment_amount
        self.lend_status = UInt64(4)

    ##############################################
    # function: claim_nft
    # arguments: None
    # purpose: claim the nft
    # post-conditions: nft claimed
    ##############################################
    @arc4.abimethod
    def claim_nft(self) -> None:
        ##########################################
        assert self.lend_status == UInt64(3), "lend_status not lent"
        ##########################################
        assert (
            Global.latest_timestamp > self.lend_date + self.lend_time
        ), "lend_time expired"
        ##########################################
        lend_asset = Asset(self.lend_asset_id)
        itxn.AssetTransfer(
            asset_amount=UInt64(1),
            asset_receiver=self.lender,
            xfer_asset=lend_asset,
            asset_close_to=lend_asset.creator,
        ).submit()
        ##########################################
        self.lend_status = UInt64(5)

    ##############################################
    # function: claim_debt
    # arguments: None
    # purpose: claim the debt
    # post-conditions: lend_status claimed
    ##############################################
    @arc4.abimethod
    def claim_debt(self) -> None:
        ##########################################
        assert self.lend_status == UInt64(4), "lend_status not claimed"
        assert self.lend_paid > 0, "lend_paid accurate"
        ##########################################
        itxn.Payment(amount=self.lend_payback, receiver=self.lender).submit()
        ##########################################
        self.lend_status = UInt64(5)


class NNTAssetLending(AssetLendingBase):
    ##############################################
    # function: setup
    # purpose: prepare for lending
    # pre-conditions:
    # - lend_status is 0
    # post-conditions:
    # - lend_payment_asset set
    # - lend_asset set
    # - lend_payback set
    # - lend_time set
    # - lender set
    # - lend_amount set
    # notes:
    # - should be called by app creator
    ##############################################
    @arc4.abimethod
    def setup(
        self,
        lend_type: UInt64,
        lend_payment_asset_id: UInt64,
        lend_asset_id: UInt64,
    ) -> None:
        ##########################################
        assert self.lend_status == UInt64(0), "lend_status not initialized"
        ##########################################
        lend_payment_asset = Asset(lend_payment_asset_id)
        lend_asset = Asset(lend_asset_id)
        assert (
            lend_payment_asset_id != lend_asset_id
        ), "lend_payment_asset_id not equal to lend_asset_id"
        assert (
            lend_payment_asset.clawback == Global.zero_address
        ), "lend_payment_asset not clawback"
        assert (
            lend_payment_asset.freeze == Global.zero_address
        ), "lend_payment_asset not freeze"
        assert lend_asset.clawback == Global.zero_address, "lend_asset not clawback"
        assert lend_asset.freeze == Global.zero_address, "lend_asset not freeze"
        ##########################################
        app_asset_opt_in(lend_payment_asset)
        app_asset_opt_in(lend_asset)
        ##########################################
        self.lend_type = UInt64(2)
        self.lend_payment_asset_id = lend_payment_asset_id
        self.lend_asset_id = lend_asset_id
        self.lend_status = UInt64(1)

    ##############################################
    # function: fund
    # arguments:
    # - lend_payback, the amount to pay back
    # - lend_time, the time to pay back
    # purpose: fund the contract
    # post-conditions: lend_status funded
    ##############################################
    @arc4.abimethod
    def fund(
        self,
        lend_amount: arc4.UInt64,
        lend_payback: arc4.UInt64,
        lend_time: arc4.UInt64,
    ) -> None:
        ##########################################
        assert self.lend_status == UInt64(1), "lend_status not setup"
        ##########################################
        lender = Txn.sender
        lend_payment_asset = Asset(self.lend_payment_asset_id)
        payment_amount = require_asset_transfer(
            Txn.sender, UInt64(1), lend_payment_asset
        )
        assert payment_amount == lend_amount, "payment amount accurate"
        assert payment_amount > UInt64(2000000), "payment amount accurate"
        assert lend_payback > payment_amount + UInt64(2000000), "lend_payback accurate"
        assert lend_time > UInt64(0), "lend_time accurate"
        ##########################################
        self.lender = lender
        self.lend_amount = payment_amount
        self.lend_payback = lend_payback.native
        self.lend_time = lend_time.native
        self.lend_status = UInt64(2)

    ##############################################
    # function: pay_debt
    # arguments: None
    # purpose: pay dept
    # post-conditions: lend_status paid
    ##############################################
    @arc4.abimethod
    def pay_debt(self) -> None:
        ##########################################
        assert self.lend_status == UInt64(3), "lend_status not lent"
        ##########################################
        assert Txn.sender == self.borrower, "sender accurate"
        lend_payment_asset = Asset(self.lend_payment_asset_id)
        payment_amount = require_asset_transfer(
            Txn.sender, UInt64(1), lend_payment_asset
        )
        assert payment_amount == self.lend_payback, "payment amount accurate"
        ##########################################
        lend_asset = Asset(self.lend_asset_id)
        itxn.AssetTransfer(
            asset_amount=UInt64(1),
            asset_receiver=self.borrower,
            xfer_asset=lend_asset,
            asset_close_to=lend_asset.creator,
        ).submit()
        ##########################################
        self.lend_paid = payment_amount
        self.lend_status = UInt64(4)

    ##############################################
    # function: claim_nft
    # arguments: None
    # purpose: claim the nft
    # post-conditions: nft claimed
    ##############################################
    @arc4.abimethod
    def claim_nft(self) -> None:
        ##########################################
        assert self.lend_status == UInt64(3), "lend_status not lent"
        ##########################################
        assert Txn.sender == self.lender, "sender accurate"
        assert (
            Global.latest_timestamp > self.lend_date + self.lend_time
        ), "lend_time expired"
        ##########################################
        lend_payment_asset = Asset(self.lend_payment_asset_id)
        lend_asset = Asset(self.lend_asset_id)
        itxn.AssetTransfer(
            asset_amount=UInt64(1),
            asset_receiver=self.lender,
            xfer_asset=lend_asset,
            asset_close_to=lend_asset.creator,
        ).submit()
        itxn.AssetTransfer(
            asset_amount=UInt64(0),
            asset_receiver=self.lender,
            xfer_asset=lend_payment_asset,
            asset_close_to=lend_payment_asset.creator,
        ).submit()
        ##########################################
        self.lend_status = UInt64(5)

    ##############################################
    # function: claim_debt
    # arguments: None
    # purpose: claim the debt
    # post-conditions: lend_status claimed
    ##############################################
    @arc4.abimethod
    def claim_debt(self) -> None:
        ##########################################
        assert self.lend_status == UInt64(4), "lend_status not claimed"
        assert self.lend_paid > 0, "lend_paid accurate"
        ##########################################
        assert Txn.sender == self.lender, "sender accurate"
        lend_payment_asset = Asset(self.lend_payment_asset_id)
        itxn.AssetTransfer(
            asset_amount=self.lend_payback,
            asset_receiver=self.lender,
            xfer_asset=lend_payment_asset,
            asset_close_to=lend_payment_asset.creator,
        ).submit()
        ##########################################
        self.lend_status = UInt64(5)


class SmartAssetLending(AssetLendingBase):
    ##############################################
    # function: setup
    # arguments:
    # - lend_type, the type of lending
    # - lend_payment_asset_id, the asset to be lent
    # - lend_asset_id, the asset to be paid back
    # purpose: setup lending
    # post-conditions: lend_status setup
    ##############################################
    @arc4.abimethod
    def setup(
        self,
        lend_type: UInt64,
        lend_payment_asset_id: UInt64,
        lend_asset_id: UInt64,
    ) -> None:
        ##########################################
        assert self.lend_status == UInt64(0), "lend_status not initialized"
        ##########################################
        lend_asset = Asset(lend_asset_id)
        assert lend_asset.clawback == Global.zero_address, "lend_asset not clawback"
        assert lend_asset.freeze == Global.zero_address, "lend_asset not freeze"
        ##########################################
        app_asset_opt_in(lend_asset)
        ##########################################
        self.lend_type = UInt64(3)
        self.lend_payment_asset_id = lend_payment_asset_id
        self.lend_asset_id = lend_asset_id
        self.lend_status = UInt64(1)

    ##############################################
    # function: fund
    # arguments:
    # - lend_payback, the amount to pay back
    # - lend_time, the time to pay back
    # purpose: fund the contract
    # post-conditions: lend_status funded
    ##############################################
    @arc4.abimethod
    def fund(
        self,
        lend_amount: arc4.UInt64,
        lend_payback: arc4.UInt64,
        lend_time: arc4.UInt64,
    ) -> None:
        ##########################################
        assert self.lend_status == UInt64(1), "lend_status not setup"
        ##########################################
        lender = Txn.sender
        arc200_balanceOf_call = itxn.ApplicationCall(
            app_id=self.lend_payment_asset_id,
            app_args=(
                arc4.arc4_signature("arc200_balanceOf(address)uint256"),
                Txn.sender,
            ),
        ).submit()
        arc200_balanceOf = arc4.UInt256.from_log(arc200_balanceOf_call.last_log)
        assert arc200_balanceOf >= lend_amount, "arc200_balanceOf accurate"
        arc200_allowance_call = itxn.ApplicationCall(
            app_id=self.lend_payment_asset_id,
            app_args=(
                arc4.arc4_signature("arc200_allowance(address,address)uint256"),
                Txn.sender,
                Global.current_application_address,
            ),
        ).submit()
        arc200_allowance = arc4.UInt256.from_log(arc200_allowance_call.last_log)
        assert arc200_allowance >= lend_amount, "arc200_allowance accurate"
        assert lend_payback > lend_amount, "lend_payback accurate"
        assert lend_time > UInt64(0), "lend_time accurate"
        # #########################################
        self.lender = lender
        self.lend_amount = lend_amount.native
        self.lend_payback = lend_payback.native
        self.lend_time = lend_time.native
        self.lend_status = UInt64(2)

    ##############################################
    # function: lend_nft
    # arguments: None
    # purpose: lend the nft
    # post-conditions: lend_status lent
    ##############################################
    @arc4.abimethod
    def lend_nft(
        self,
    ) -> None:
        ##########################################
        assert self.lend_status == UInt64(2), "lend_status not funded"
        ##########################################
        lend_asset = Asset(self.lend_asset_id)
        axfer_amount = require_asset_transfer(Txn.sender, UInt64(1), lend_asset)
        assert axfer_amount == UInt64(1), "axfer amount accurate"
        ##########################################
        borrower = Txn.sender
        itxn.ApplicationCall(
            app_id=self.lend_payment_asset_id,
            app_args=(
                arc4.arc4_signature("arc200_transferFrom(address,address)bool"),
                self.lender,
                Txn.sender,
            ),
        ).submit()
        ##########################################
        self.borrower = borrower
        self.lend_date = Global.latest_timestamp
        self.lend_status = UInt64(3)

    ##############################################
    # function: pay_debt
    # arguments: None
    # purpose: pay dept
    # post-conditions: lend_status paid
    ##############################################
    @arc4.abimethod
    def pay_debt(self) -> None:
        ##########################################
        assert self.lend_status == UInt64(3), "lend_status not lent"
        ##########################################
        assert Txn.sender == self.borrower, "sender accurate"
        ##########################################
        itxn.ApplicationCall(
            app_id=self.lend_payment_asset_id,
            app_args=(
                arc4.arc4_signature("arc200_transferFrom(address,address)bool"),
                self.borrower,
                self.lender,
                self.lend_payback,
            ),
        ).submit()
        lend_asset = Asset(self.lend_asset_id)
        itxn.AssetTransfer(
            asset_amount=UInt64(1),
            asset_receiver=self.borrower,
            xfer_asset=lend_asset,
            asset_close_to=lend_asset.creator,
        ).submit()
        ##########################################
        self.lend_paid = self.lend_payback
        self.lend_status = UInt64(5)

    ##############################################
    # function: claim_nft
    # arguments: None
    # purpose: claim the nft
    # post-conditions: lend_status claimed
    ##############################################
    @arc4.abimethod
    def claim_nft(self) -> None:
        ##########################################
        assert self.lend_status == UInt64(3), "lend_status not lent"
        ##########################################
        assert (
            Global.latest_timestamp > self.lend_date + self.lend_time
        ), "lend_time expired"
        ##########################################
        lend_asset = Asset(self.lend_asset_id)
        itxn.AssetTransfer(
            asset_amount=UInt64(1),
            asset_receiver=self.lender,
            xfer_asset=lend_asset,
            asset_close_to=lend_asset.creator,
        ).submit()
        ##########################################
        self.lend_status = UInt64(5)

    ##############################################
    # function: claim_debt
    # arguments: None
    # purpose: claim the debt
    # post-conditions: lend_status claimed
    ##############################################
    @arc4.abimethod
    def claim_debt(self) -> None:
        pass
