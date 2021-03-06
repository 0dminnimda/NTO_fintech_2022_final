// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

struct Sign {
    uint8 v;
    bytes32 r;
    bytes32 s;
}

contract RentalAgreement {
    uint256 roomInternalId_;
    uint256 deadline_;
    uint256 rentalRate_;
    uint256 billingPeriodDuration_;
    uint256 billingsCount_;
    uint256 rentStartTime_;
    uint256 rentEndTime_;
    uint256 currentProfit_ = 0;
    uint256 currentBillingPeriod_ = 0;
    uint256 totalLandlordWithdrawals_ = 0;

    address payable landLord_;
    address payable tenant_;

    bytes32 private DOMAIN_SEPARATOR;
    bytes32 private constant PERMIT_TYPEHASH = keccak256("RentalPermit(uint256 deadline,address tenant,uint256 rentalRate,uint256 billingPeriodDuration,uint256 billingsCount)");
    bytes32 private constant TICKET_TYPEHASH = keccak256("Ticket(uint256 deadline,uint256 nonce,uint256 value)");
    bytes32 private constant END_TYPEHASH = keccak256("EndConsent(uint256 deadline)");

    address[] private cashiers;
    mapping(address => uint256) private cashierNonce;
    mapping(address => bool) private cashierStatus;

    event PurchasePayment(uint256 amount);

    constructor (uint256 roomInternalId) {
        landLord_ = payable(msg.sender);
        roomInternalId_ = roomInternalId;
        DOMAIN_SEPARATOR = keccak256(abi.encode(
            keccak256("EIP712Domain(string name,string version,address verifyingContract)"),
            keccak256(bytes("Rental Agreement")),
            keccak256(bytes("1.0")),
            address(this)
        ));
    }

    function rent (uint256 deadline, address payable tenant, uint256 rentalRate, uint256 billingPeriodDuration, uint256 billingsCount, Sign calldata landlordSign) payable public {
        if (tenant_ != address(0)) revert("The contract is being in not allowed state");

        bytes32 digest = keccak256(abi.encodePacked(
            "\x19\x01",
            DOMAIN_SEPARATOR,
            keccak256(abi.encode(
                PERMIT_TYPEHASH,
                deadline,
                tenant,
                rentalRate,
                billingPeriodDuration,
                billingsCount
            ))
        ));
        if (landLord_ != ecrecover(digest, landlordSign.v, landlordSign.r, landlordSign.s)) revert("Invalid landlord sign");

        if (deadline < block.timestamp) revert("The operation is outdated");
        if (tenant != msg.sender) revert("The caller account and the account specified as a tenant do not match");
        if (landLord_ == tenant) revert("The landlord cannot become a tenant");
        if (rentalRate <= 0) revert("Rent amount should be strictly greater than zero");
        if (billingPeriodDuration <= 0) revert("Rent period should be strictly greater than zero");
        if (billingsCount <= 0) revert("Rent period repeats should be strictly greater than zero");
        if (msg.value < rentalRate) revert("Incorrect deposit");

        deadline_ = deadline;
        tenant_ = tenant;
        rentalRate_ = rentalRate;
        billingPeriodDuration_ = billingPeriodDuration;
        billingsCount_ = billingsCount;
        rentStartTime_ = block.timestamp;
        rentEndTime_ = rentStartTime_ + billingPeriodDuration * billingsCount;
    }

    function addCashier (address addr) public {
        if (msg.sender != tenant_) revert("You are not a tenant");
        if (addr == landLord_) revert("The landlord cannot become a cashier");
        if (addr == address(0)) revert("Zero address cannot become a cashier");

        cashiers.push(addr);
        cashierNonce[addr] += 1;
        cashierStatus[addr] = true;
    }

    function removeCashier (address cashierAddr) public {
        if (msg.sender != tenant_) revert("You are not a tenant");
        if (!cashierStatus[cashierAddr]) revert("Unknown cashier");

        for (uint256 i = 0; i < cashiers.length; i += 1) {
            if (cashiers[i] == cashierAddr) {
                cashiers[i] = cashiers[cashiers.length - 1];
                cashiers.pop();
                cashierStatus[cashierAddr] = false;
                return;
            }
        }
    }

    function getCashierNonce (address cashierAddr) view public returns (uint) {
        if (cashierStatus[cashierAddr]) return cashierNonce[cashierAddr];
        return 0;
    }

    function getCashiersList () view public returns (address[] memory) { return cashiers; }

    function pay (uint256 deadline, uint256 nonce, uint256 value, Sign calldata cashierSign) payable public {
        if (rentEndTime_ <= block.timestamp) revert("The contract is being in not allowed state");
        uint256 newBillingPeriod = (block.timestamp - rentStartTime_) / billingPeriodDuration_;
        if (currentBillingPeriod_ != newBillingPeriod) {
            if (currentProfit_ < rentalRate_ || newBillingPeriod - currentBillingPeriod_ > 1) revert("The contract is being in not allowed state");
            else {
                currentProfit_ = 0;
                currentBillingPeriod_ = newBillingPeriod;
            }
        }

        if (deadline < block.timestamp) revert("The operation is outdated");
        bytes32 digest = keccak256(abi.encodePacked(
            "\x19\x01",
            DOMAIN_SEPARATOR,
            keccak256(abi.encode(
                TICKET_TYPEHASH,
                deadline,
                nonce,
                value
            ))
        ));
        address cashier = ecrecover(digest, cashierSign.v, cashierSign.r, cashierSign.s);

        if (!cashierStatus[cashier]) revert("Unknown cashier");
        if (cashierNonce[cashier] != nonce) revert("Invalid nonce");
        if (value != msg.value) revert("Invalid value");

        cashierNonce[cashier] += 1;
        currentProfit_ += msg.value;
        emit PurchasePayment(value);
    }

    function getTenantProfit () view public returns (uint256) {
        uint256 newBillingPeriod = (block.timestamp - rentStartTime_) / billingPeriodDuration_;
        if (newBillingPeriod >= billingsCount_) newBillingPeriod = billingsCount_ - 1;

        if (newBillingPeriod == billingsCount_ - 1 || currentBillingPeriod_ < newBillingPeriod) return address(this).balance - getLandlordProfit();
        if (currentProfit_ < rentalRate_) return address(this).balance - getLandlordProfit() - currentProfit_;
        return address(this).balance - getLandlordProfit() - rentalRate_;
    }

    function withdrawTenantProfit () public {
        uint256 profit = getTenantProfit();
        if (profit > 0) tenant_.transfer(profit);
    }

    function getLandlordProfit () view public returns (uint256)  {
        uint256 newBillingPeriod = (block.timestamp - rentStartTime_) / billingPeriodDuration_;
        if (newBillingPeriod >= billingsCount_) newBillingPeriod = billingsCount_ - 1;

        if (currentBillingPeriod_ == newBillingPeriod || (newBillingPeriod - currentBillingPeriod_ == 1 && currentProfit_ >= rentalRate_)) return (newBillingPeriod + 1) * rentalRate_ - totalLandlordWithdrawals_;
        return (currentBillingPeriod_ + 1) * rentalRate_ + currentProfit_ - totalLandlordWithdrawals_;

    }

    function withdrawLandlordProfit () public {
        uint256 profit = getLandlordProfit();
        if (profit > 0) {
            landLord_.transfer(profit);
            totalLandlordWithdrawals_ += profit;
        }
    }

    function endAgreement () public {
        if (tenant_ == address(0)) revert("The contract is being in not allowed state");

        if (block.timestamp >= rentEndTime_) {
            withdrawLandlordProfit();
            selfdestruct(tenant_);
        }
        else {
            uint256 newBillingPeriod = (block.timestamp - rentStartTime_) / billingPeriodDuration_;
            if (currentBillingPeriod_ == newBillingPeriod || (newBillingPeriod - currentBillingPeriod_ == 1 && currentProfit_ >= rentalRate_)) revert("The contract is being in not allowed state");
            else {
                withdrawTenantProfit();
                selfdestruct(landLord_);
            }
        }
    }

    function endAgreementManually (uint256 deadline, Sign calldata landlordSign, Sign calldata tenantSign) public {
        if (tenant_ == address(0)) revert("The contract is being in not allowed state");
        if (deadline < block.timestamp) revert("The operation is outdated");

        bytes32 digest = keccak256(abi.encodePacked(
            "\x19\x01",
            DOMAIN_SEPARATOR,
            keccak256(abi.encode(END_TYPEHASH, deadline))
        ));
        address landlord = ecrecover(digest, landlordSign.v, landlordSign.r, landlordSign.s);
        if (landlord != landLord_) revert("Invalid landlord sign");

        digest = keccak256(abi.encodePacked(
            "\x19\x01",
            DOMAIN_SEPARATOR,
            keccak256(abi.encode(END_TYPEHASH, deadline))
        ));
        address tenant = ecrecover(digest, tenantSign.v, tenantSign.r, tenantSign.s);
        if (tenant != tenant_) revert("Invalid tenant sign");

        withdrawLandlordProfit();
        selfdestruct(tenant_);
    }

    function getRoomInternalId () view public returns (uint) { return roomInternalId_; }

    function getLandlord () view public returns (address)  { return landLord_; }

    function getTenant () view public returns (address)  { return tenant_; }

    function getBillingPeriodDuration () view public returns (uint)  { return billingPeriodDuration_; }

    function getRentStartTime () view public returns (uint) { return rentStartTime_; }

    function getRentEndTime () view public returns (uint)  { return rentEndTime_; }

    function getRentalRate () view public returns (uint)  { return rentalRate_; }
}
