/*
Navicat MySQL Data Transfer

Source Server         : win
Source Server Version : 80028
Source Host           : localhost:3306
Source Database       : flask

Target Server Type    : MYSQL
Target Server Version : 80028
File Encoding         : 65001

Date: 2022-04-21 16:55:52
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for cardtable
-- ----------------------------
DROP TABLE IF EXISTS `cardtable`;
CREATE TABLE `cardtable` (
  `id` int NOT NULL AUTO_INCREMENT,
  `phone` mediumblob,
  `describe` varchar(255) NOT NULL,
  `key` int NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of cardtable
-- ----------------------------
