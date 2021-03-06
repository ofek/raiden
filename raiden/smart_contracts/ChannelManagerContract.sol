pragma solidity ^0.4.11;

import "./Token.sol";
import "./ChannelManagerLibrary.sol";

// for each token a manager will be deployed, to reduce gas usage for manager
// deployment the logic is moved into a library and this contract will work
// only as a proxy/state container.
contract ChannelManagerContract {
    using ChannelManagerLibrary for ChannelManagerLibrary.Data;
    ChannelManagerLibrary.Data data;

    event ChannelNew(
        address netting_channel,
        address participant1,
        address participant2,
        uint settle_timeout
    );

    event ChannelDeleted(
        address caller_address,
        address partner
    );

    function ChannelManagerContract(address token_address) {
        data.token = Token(token_address);
    }

    /// @notice Get all channels
    /// @return All the open channels
    function getChannelsAddresses() constant returns (address[]) {
        return data.all_channels;
    }

    /// @notice Get all participants of all channels
    /// @return All participants in all channels
    function getChannelsParticipants() constant returns (address[]) {
        uint i;
        uint pos;
        address[] memory result;
        NettingChannelContract channel;

        result = new address[](data.all_channels.length * 2);

        pos = 0;
        for (i = 0; i < data.all_channels.length; i++) {
            channel = NettingChannelContract(data.all_channels[i]);

            var (address1, , address2, ) = channel.addressAndBalance();

            result[pos] = address1;
            pos += 1;
            result[pos] = address2;
            pos += 1;
        }

        return result;
    }

    /// @notice Get all channels that an address participates in.
    /// @param node_address The address of the node
    /// @return The channel's addresses that node_address participates in.
    function nettingContractsByAddress(address node_address) constant returns (address[]) {
        return data.nodeaddress_to_channeladdresses[node_address];
    }

    /// @notice Get the address of the channel token
    /// @return The token
    function tokenAddress() constant returns (address) {
        return data.token;
    }

    /// @notice Get the address of channel with a partner
    /// @param partner The address of the partner
    /// @return The address of the channel
    function getChannelWith(address partner) constant returns (address) {
        return data.getChannelWith(partner);
    }

    /// @notice Create a new payment channel between two parties
    /// @param partner The address of the partner
    /// @param settle_timeout The settle timeout in blocks
    /// @return The address of the newly created NettingChannelContract.
    function newChannel(address partner, uint settle_timeout) returns (address) {
        address old_channel = getChannelWith(partner);
        if (old_channel != 0) {
            ChannelDeleted(msg.sender, partner);
        }

        address new_channel = data.newChannel(partner, settle_timeout);
        ChannelNew(new_channel, msg.sender, partner, settle_timeout);
        return new_channel;
    }

    function () { revert(); }
}
