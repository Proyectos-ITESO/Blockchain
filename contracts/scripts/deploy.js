/**
 * Deployment script for Notary contract
 * Usage: npx hardhat run scripts/deploy.js --network sepolia
 */
const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("Deploying Notary contract...");

  // Get the contract factory
  const Notary = await hre.ethers.getContractFactory("Notary");

  // Deploy the contract
  const notary = await Notary.deploy();

  await notary.waitForDeployment();

  const address = await notary.getAddress();

  console.log(`Notary contract deployed to: ${address}`);
  console.log(`Network: ${hre.network.name}`);

  // Save contract address and ABI to file
  const deploymentInfo = {
    address: address,
    network: hre.network.name,
    chainId: (await hre.ethers.provider.getNetwork()).chainId,
    deployedAt: new Date().toISOString()
  };

  // Save deployment info
  const deploymentsDir = path.join(__dirname, '../deployments');
  if (!fs.existsSync(deploymentsDir)) {
    fs.mkdirSync(deploymentsDir, { recursive: true });
  }

  fs.writeFileSync(
    path.join(deploymentsDir, `${hre.network.name}.json`),
    JSON.stringify(deploymentInfo, null, 2)
  );

  console.log(`Deployment info saved to deployments/${hre.network.name}.json`);

  // Save ABI to Python backend directory
  const artifactPath = path.join(__dirname, '../artifacts/Notary.sol/Notary.json');
  const artifact = JSON.parse(fs.readFileSync(artifactPath, 'utf8'));

  const backendDir = path.join(__dirname, '../../app/services');
  fs.writeFileSync(
    path.join(backendDir, 'notary_abi.json'),
    JSON.stringify(artifact.abi, null, 2)
  );

  console.log('ABI saved to app/services/notary_abi.json');

  // If on testnet, wait for confirmations and verify
  if (hre.network.name !== "hardhat" && hre.network.name !== "localhost") {
    console.log("Waiting for 5 block confirmations...");
    await notary.deploymentTransaction().wait(5);
    console.log("Contract confirmed!");

    console.log("\nTo verify on Etherscan, run:");
    console.log(`npx hardhat verify --network ${hre.network.name} ${address}`);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
