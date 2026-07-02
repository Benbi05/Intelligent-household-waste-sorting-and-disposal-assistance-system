-- 垃圾分类系统 数据库结构
-- 导出: 2026-07-01

CREATE DATABASE IF NOT EXISTS garbage_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE garbage_system;


CREATE TABLE `administrator` (
  `id` int NOT NULL AUTO_INCREMENT,
  `userId` int NOT NULL,
  `username` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `passwordHash` varchar(256) COLLATE utf8mb4_unicode_ci NOT NULL,
  `role` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `community` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT '',
  `lastLoginTime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `userId` (`userId`),
  UNIQUE KEY `username` (`username`),
  CONSTRAINT `administrator_ibfk_1` FOREIGN KEY (`userId`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `analysis_report` (
  `reportId` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `statMonth` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL,
  `statArea` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `reportType` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `consumeTrend` text COLLATE utf8mb4_unicode_ci,
  `hotProducts` text COLLATE utf8mb4_unicode_ci,
  `suggestion` text COLLATE utf8mb4_unicode_ci,
  `fullContent` text COLLATE utf8mb4_unicode_ci,
  `generateTime` datetime DEFAULT NULL,
  `generateDuration` int DEFAULT NULL,
  PRIMARY KEY (`reportId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `area` (
  `id` int NOT NULL AUTO_INCREMENT,
  `areaName` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `deviceCount` int DEFAULT NULL,
  `status` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `areaName` (`areaName`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `commodity` (
  `id` int NOT NULL AUTO_INCREMENT,
  `commodityName` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `merchantId` int NOT NULL,
  `pointPrice` int NOT NULL,
  `stock` int DEFAULT NULL,
  `imageUrl` varchar(512) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `useRules` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `monthExchangeCount` int DEFAULT NULL,
  `version` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `merchantId` (`merchantId`),
  CONSTRAINT `commodity_ibfk_1` FOREIGN KEY (`merchantId`) REFERENCES `merchant` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `delivery_record` (
  `recordId` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `deviceId` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `userId` int NOT NULL,
  `imageUrl` varchar(512) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `boxCategory` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `garbageCategory` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `parentType` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `isCorrect` tinyint(1) DEFAULT NULL,
  `pointChange` int DEFAULT NULL,
  `weight` float DEFAULT NULL,
  `deliveryTime` datetime DEFAULT NULL,
  `ruleVersion` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`recordId`),
  KEY `deviceId` (`deviceId`),
  KEY `userId` (`userId`),
  CONSTRAINT `delivery_record_ibfk_1` FOREIGN KEY (`deviceId`) REFERENCES `device` (`deviceId`),
  CONSTRAINT `delivery_record_ibfk_2` FOREIGN KEY (`userId`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `device` (
  `deviceId` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `deviceName` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `deviceSecret` varchar(256) COLLATE utf8mb4_unicode_ci NOT NULL,
  `boxCategory` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `area` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `location` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `onlineStatus` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fullRate` float DEFAULT NULL,
  `cameraStatus` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `networkStatus` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `powerStatus` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `displayStatus` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `firmwareVersion` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `lastOnlineTime` datetime DEFAULT NULL,
  `totalDeliveryCount` int DEFAULT NULL,
  `todayDeliveryCount` int DEFAULT NULL,
  `lat` double DEFAULT NULL,
  `lng` double DEFAULT NULL,
  PRIMARY KEY (`deviceId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `garbage_category` (
  `categoryId` int NOT NULL AUTO_INCREMENT,
  `categoryName` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `parentType` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `parentTypeName` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `rewardPoint` int DEFAULT NULL,
  `penaltyPoint` int DEFAULT NULL,
  `guide` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`categoryId`)
) ENGINE=InnoDB AUTO_INCREMENT=901 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `merchant` (
  `id` int NOT NULL AUTO_INCREMENT,
  `userId` int NOT NULL,
  `username` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `passwordHash` varchar(256) COLLATE utf8mb4_unicode_ci NOT NULL,
  `storeName` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `contactName` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `contactPhone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `storeAddress` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `businessLicense` text COLLATE utf8mb4_unicode_ci,
  `idCard` text COLLATE utf8mb4_unicode_ci,
  `area` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `status` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `auditTime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `userId` (`userId`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `storeName` (`storeName`),
  CONSTRAINT `merchant_ibfk_1` FOREIGN KEY (`userId`) REFERENCES `user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `operation_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `adminId` int NOT NULL,
  `adminName` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `actionType` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `targetId` int DEFAULT NULL,
  `detail` text COLLATE utf8mb4_unicode_ci,
  `ip` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `createTime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `permKey` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `permName` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `group` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `permKey` (`permKey`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `point_account` (
  `id` int NOT NULL AUTO_INCREMENT,
  `userId` int NOT NULL,
  `balance` int DEFAULT NULL,
  `totalEarned` int DEFAULT NULL,
  `totalSpent` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `userId` (`userId`),
  CONSTRAINT `point_account_ibfk_1` FOREIGN KEY (`userId`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `point_order` (
  `orderId` varchar(32) COLLATE utf8mb4_unicode_ci NOT NULL,
  `userId` int NOT NULL,
  `commodityId` int NOT NULL,
  `merchantId` int NOT NULL,
  `pointCost` int NOT NULL,
  `quantity` int DEFAULT NULL,
  `verifyCode` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `orderStatus` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `idempotentKey` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `createTime` datetime DEFAULT NULL,
  `verifyTime` datetime DEFAULT NULL,
  `expireTime` datetime NOT NULL,
  PRIMARY KEY (`orderId`),
  UNIQUE KEY `verifyCode` (`verifyCode`),
  KEY `userId` (`userId`),
  KEY `commodityId` (`commodityId`),
  KEY `merchantId` (`merchantId`),
  CONSTRAINT `point_order_ibfk_1` FOREIGN KEY (`userId`) REFERENCES `user` (`id`),
  CONSTRAINT `point_order_ibfk_2` FOREIGN KEY (`commodityId`) REFERENCES `commodity` (`id`),
  CONSTRAINT `point_order_ibfk_3` FOREIGN KEY (`merchantId`) REFERENCES `merchant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `point_record` (
  `id` int NOT NULL AUTO_INCREMENT,
  `userId` int NOT NULL,
  `changeAmount` int NOT NULL,
  `recordType` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL,
  `reason` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `relatedId` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `createTime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `userId` (`userId`),
  CONSTRAINT `point_record_ibfk_1` FOREIGN KEY (`userId`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `recognition_model` (
  `modelId` int NOT NULL AUTO_INCREMENT,
  `version` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL,
  `accuracy` float DEFAULT NULL,
  `mapValue` float DEFAULT NULL,
  `precision` float DEFAULT NULL,
  `recall` float DEFAULT NULL,
  `categoryCount` int DEFAULT NULL,
  `status` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `modelPath` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `publishTime` datetime DEFAULT NULL,
  PRIMARY KEY (`modelId`),
  UNIQUE KEY `version` (`version`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `recommendation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `merchantId` int NOT NULL,
  `community` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `content` text COLLATE utf8mb4_unicode_ci,
  `products` text COLLATE utf8mb4_unicode_ci,
  `status` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `createTime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `merchantId` (`merchantId`),
  CONSTRAINT `recommendation_ibfk_1` FOREIGN KEY (`merchantId`) REFERENCES `merchant` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `resident` (
  `id` int NOT NULL AUTO_INCREMENT,
  `userId` int NOT NULL,
  `totalDeliveryTimes` int DEFAULT NULL,
  `correctTimes` int DEFAULT NULL,
  `correctRate` float DEFAULT NULL,
  `area` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `userId` (`userId`),
  CONSTRAINT `resident_ibfk_1` FOREIGN KEY (`userId`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `role` (
  `id` int NOT NULL AUTO_INCREMENT,
  `roleName` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `permissions` text COLLATE utf8mb4_unicode_ci,
  `description` varchar(256) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `roleName` (`roleName`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `sub_account` (
  `id` int NOT NULL AUTO_INCREMENT,
  `merchantId` int NOT NULL,
  `username` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL,
  `passwordHash` varchar(256) COLLATE utf8mb4_unicode_ci NOT NULL,
  `displayName` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `permissions` text COLLATE utf8mb4_unicode_ci,
  `status` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `merchantId` (`merchantId`),
  CONSTRAINT `sub_account_ibfk_1` FOREIGN KEY (`merchantId`) REFERENCES `merchant` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `user` (
  `openid` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `phone` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `nickName` varchar(64) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `avatarUrl` varchar(512) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(16) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `userType` varchar(16) COLLATE utf8mb4_unicode_ci NOT NULL,
  `id` int NOT NULL AUTO_INCREMENT,
  `createTime` datetime NOT NULL,
  `updateTime` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `openid` (`openid`),
  UNIQUE KEY `phone` (`phone`)
) ENGINE=InnoDB AUTO_INCREMENT=1098 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;