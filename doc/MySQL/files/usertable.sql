/*
Navicat MySQL Data Transfer

Source Server         : win
Source Server Version : 80028
Source Host           : localhost:3306
Source Database       : flask

Target Server Type    : MYSQL
Target Server Version : 80028
File Encoding         : 65001

Date: 2022-04-21 16:56:10
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for usertable
-- ----------------------------
DROP TABLE IF EXISTS `usertable`;
CREATE TABLE `usertable` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(255) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `nickname` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Records of usertable
-- ----------------------------
INSERT INTO `usertable` VALUES ('1', 'Langery', '123456', 'Langery');
INSERT INTO `usertable` VALUES ('2', '1', '1', '1');
