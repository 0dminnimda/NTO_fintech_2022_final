// SPDX-License-Identifier: MIT
pragma solidity ^0.8.11;

struct Sign {
    uint8 v;
    bytes32 r;
    bytes32 s;
}

struct EIP712Domain {
    string name;
    string version;
    address verifyingContract;
}

struct RentalPermit {
    uint256 deadline;
    address tenant;
    uint256 rentalRate;
    uint256 billingPeriodDuration;
    uint256 billingsCount;
}

bytes32 constant EIP712Domain_TYPEHASH = keccak256("EIP712Domain(string name,string version,address verifyingContract)");
bytes32 constant RentalPermit_TYPEHASH = keccak256("RentalPermit(uint256 deadline,address tenant,uint256 rentalRate,uint256 billingPeriodDuration,uint256 billingsCount)");

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
    bytes32 DOMAIN_SEPARATOR;

    constructor (uint roomInternalId) {
        landLord_ = msg.sender;
        roomInternalId_ = roomInternalId;
        DOMAIN_SEPARATOR = hash(EIP712Domain({
            name: "Rental Agreement",
            version: '1.0',
            verifyingContract: address(this)
        }));
    }

    function hash(EIP712Domain memory domain) internal pure returns (bytes32) {
        return keccak256(abi.encode(
            EIP712Domain_TYPEHASH,
            keccak256(bytes(domain.name)),
            keccak256(bytes(domain.version)),
            domain.verifyingContract
        ));
    }

    function hash(RentalPermit memory rp) internal pure returns (bytes32) {
        return keccak256(abi.encode(
            RentalPermit_TYPEHASH,
            rp.deadline,
            rp.tenant,
            rp.rentalRate,
            rp.billingPeriodDuration,
            rp.billingsCount
        ));
    }

    function verify(RentalPermit memory rp, uint8 v, bytes32 r, bytes32 s) internal view returns (bool) {
        bytes32 digest = keccak256(abi.encodePacked(
            "\x19\x01",
            DOMAIN_SEPARATOR,
            hash(rp)
        ));
        return ecrecover(digest, v, r, s) == landLord_;
    }

    function rent (uint deadline, address tenant, uint rentalRate, uint billingPeriodDuration, uint billingsCount, Sign calldata landlordSign) payable public {
        if (tenant_ != address(0)) revert("The contract is being in not allowed state");
        if (!verify(
            RentalPermit(deadline, tenant, rentalRate, billingPeriodDuration, billingsCount),
            landlordSign.v,
            landlordSign.r,
            landlordSign.s
        )) revert("Invalid landlord sign");

        if (deadline > block.timestamp) revert("The operation is outdated");
        if (tenant != msg.sender) revert("The caller account and the account specified as a tenant do not match");
        if (landLord_ == tenant) revert("The landlord cannotbecome a tenant");
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

    function getRoomInternalId () view public returns (uint) { return roomInternalId_; }

    function getLandlord () view public returns (address)  { return landLord_; }

    function getTenant () view public returns (address)  { return tenant_; }

    function getBillingPeriodDuration () view public returns (uint)  { return billingPeriodDuration_; }

    function getRentStartTime () view public returns (uint) { return rentStartTime_; }

    function getRentEndTime () view public returns (uint)  { return rentEndTime_; }

    function getRentalRate () view public returns (uint)  { return rentalRate_; }
}
