// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

struct Sign {
    uint8 v;
    bytes32 r;
    bytes32 s;
}

contract RentalAgreement {
    uint roomInternalId_;
    uint deadline_;
    uint rentalRate_;
    uint billingPeriodDuration_;
    uint billingsCount_;
    uint rentStartTime_;
    uint rentEndTime_;
    address landLord_;
    address tenant_;

    constructor (uint roomInternalId) {
        landLord_ = msg.sender;
        roomInternalId_ = roomInternalId;
    }

    function rent (uint deadline, address tenant, uint rentalRate, uint billingPeriodDuration, uint billingsCount, Sign calldata landlordSign) payable public {
        if (tenant_) revert("The contract is being in not allowed state");

        deadline_ = deadline;
        tenant_ = tenant;
        rentalRate_ = rentalRate;
        billingPeriodDuration_ = billingPeriodDuration;
        billingsCount_ = billingsCount;
        rentStartTime_ = block.timestamp;
        rentEndTime_ = rentStartTime_ + billingPeriodDuration * billingsCount;
    }

    function getRoomInternalId () view public returns (uint) { return roomInternalId_; }

    function getLandlord () view public returns (address)  { return landLord_; }

    function getTenant () view public returns (address)  { return tenant_; }

    function getBillingPeriodDuration () view public returns (uint)  { return billingPeriodDuration_; }

    function getRentStartTime () view public returns (uint) { return rentStartTime_; }

    function getRentEndTime () view public returns (uint)  { return rentEndTime_; }

    function getRentalRate () view public returns (uint)  { return rentalRate_; }
}
