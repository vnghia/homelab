from pydantic import IPvAnyAddress, IPvAnyNetwork, TypeAdapter

IPvAnyAddressAdapter: TypeAdapter[IPvAnyAddress] = TypeAdapter(IPvAnyAddress)
IPvAnyNetworkAdapter: TypeAdapter[IPvAnyNetwork] = TypeAdapter(IPvAnyNetwork)
