package main

// ProfileConfig contains common configuration for all profiles
type ProfileConfig struct {
	PayloadIdentifier  string
	PayloadDisplayName string
	PayloadUUID        string
	CAName             string
	Filename           string
}

// SCEPConfig contains SCEP-specific configuration
type SCEPConfig struct {
	ChallengeVar string
	ProxyURLVar  string
	RenewalVar   string
	PayloadUUID  string
}

// WiFiConfig contains WiFi-specific configuration
type WiFiConfig struct {
	SSID                   string
	Hidden                 bool
	AutoJoin               bool
	EncryptionType         string   // WPA2, WPA3, Any
	EAPType                int      // 13 for EAP-TLS
	TrustedServerNames     []string
	CertificateAnchorUUIDs []string
	SCEPPayloadUUID        string
	WiFiPayloadUUID        string
}

// VPNConfig contains VPN-specific configuration
type VPNConfig struct {
	UserDefinedName      string
	ServerAddress        string
	RemoteIdentifier     string
	LocalIdentifier      string
	ServerCertCommonName string
	OnDemandEnabled      bool
	OnDemandRules        []OnDemandRule
	IncludeAllNetworks   bool
	ExcludeLocalNetworks bool
	DeadPeerDetectionRate string // None, Low, Medium, High
	SCEPPayloadUUID      string
	VPNPayloadUUID       string
}

// OnDemandRule defines VPN on-demand behavior
type OnDemandRule struct {
	Action             string   // Connect, Disconnect, Ignore, EvaluateConnection
	DNSDomainMatch     []string
	DNSServerMatch     []string
	SSIDMatch          []string
	InterfaceTypeMatch string // WiFi, Cellular, Ethernet
	URLStringProbe     string
}

// TrustConfig contains trust profile configuration
type TrustConfig struct {
	RootCertPEM          string
	RootCertUUID         string
	IntermediateCertPEM  string
	IntermediateCertUUID string
	RADIUSCertPEM        string
	RADIUSCertUUID       string
}

// DocumentationConfig contains documentation generation parameters
type DocumentationConfig struct {
	ProfileType      string // "scep", "trust", "wifi", "vpn"
	ProfileName      string
	CAName           string
	Timestamp        string
	FleetVariables   map[string]string
	PayloadUUIDs     map[string]string
	Prerequisites    []string
	DeploymentSteps  []string
	VerificationCmds []string
	LogCommands      []string
	Notes            []string

	// Profile-specific fields
	WiFiSSID           string
	WiFiHidden         bool
	WiFiAutoJoin       bool
	WiFiEncryption     string
	TrustedServers     []string

	VPNServer          string
	VPNRemoteID        string
	VPNLocalID         string
	VPNOnDemand        bool

	HasRootCA          bool
	HasIntermediateCA  bool
	HasRADIUSCA        bool

	RootCertUUID       string
	IntermediateCertUUID string
	RADIUSCertUUID     string
	SCEPPayloadUUID    string
	WiFiPayloadUUID    string
	VPNPayloadUUID     string
}
